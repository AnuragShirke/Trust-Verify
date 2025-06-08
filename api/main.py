from fastapi import FastAPI, HTTPException, Request, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, HttpUrl, EmailStr, validator
import joblib
import os
import re
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# Import the URL scraper module
from url_scraper import get_article_from_url, is_valid_url

# Import authentication and database modules
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from database import (
    create_user, get_user_profile, create_analysis, get_analyses_by_user, get_analysis_by_id,
    create_password_reset_token, verify_reset_token, reset_password, get_user_by_email
)
from models import (
    UserCreate, UserLogin, User, Token, Analysis, UserProfile, AnalysisCreate,
    PasswordResetRequest, PasswordReset
)

# Import MLOps integration
from mlops_integration import load_models, submit_feedback, check_drift, get_model_info, MLOPS_AVAILABLE

# Define input models
class NewsInput(BaseModel):
    text: str

class UrlInput(BaseModel):
    url: str

    # Validate URL format
    @validator('url')
    def validate_url(cls, v):
        if not is_valid_url(v):
            raise ValueError('Invalid URL format. Please include http:// or https://')
        return v

class FeedbackInput(BaseModel):
    text: str
    predicted_label: int  # 0 = FAKE, 1 = REAL
    corrected_label: int  # 0 = FAKE, 1 = REAL
    source: Optional[str] = "user"

    # Validate labels
    @validator('predicted_label', 'corrected_label')
    def validate_labels(cls, v):
        if v not in [0, 1]:
            raise ValueError('Label must be 0 (FAKE) or 1 (REAL)')
        return v

# Initialize FastAPI app
app = FastAPI(
    title="Trust Verify API",
    description="API for fake news detection and trust scoring",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable CORS
# Default local origins + placeholder for production frontend URL
origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8080,https://trustverify.vercel.app,https://trust-verify-sandy.vercel.app"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory for static files if it doesn't exist
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

# Create a templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
os.makedirs(templates_dir, exist_ok=True)

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except RuntimeError:
    # If the directory is empty, this will fail, but we can ignore it
    pass

# Set up templates
try:
    templates = Jinja2Templates(directory=templates_dir)
except (RuntimeError, AssertionError, ImportError):
    # If the directory is empty or jinja2 is not installed, we'll handle it in the routes
    templates = None
    print("Warning: Jinja2 templates not available. Using fallback for root route.")

# Get the path to the parent directory (project root)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load models using MLOps integration
vectorizer, classifier, models_loaded = load_models()

# Get model information
model_info = get_model_info()
print(f"Model info: {model_info}")

# Check if MLOps is available
if MLOPS_AVAILABLE:
    print("MLOps integration is available")
else:
    print("MLOps integration is not available, using fallback methods")

# Root route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint that redirects to the API documentation.
    """
    # If templates are available, render the index page
    if templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception:
            pass

    # Otherwise, redirect to the API documentation
    return RedirectResponse(url="/docs")

# API information endpoint
@app.get("/api-info")
async def api_info():
    """
    Get information about the API.
    """
    return {
        "name": "Fake News Detector API",
        "version": "1.0.0",
        "description": "API for detecting fake news and calculating trust scores",
        "endpoints": [
            {
                "path": "/predict",
                "method": "POST",
                "description": "Predict whether a news article is real or fake",
                "parameters": {
                    "text": "The content of the news article"
                },
                "response": {
                    "prediction": "REAL or FAKE",
                    "confidence": "Confidence score (0-1)"
                }
            },
            {
                "path": "/trust-score",
                "method": "POST",
                "description": "Calculate a trust score for a news article",
                "parameters": {
                    "text": "The content of the news article"
                },
                "response": {
                    "score": "Trust score (0-100)",
                    "factors": "Breakdown of trust factors",
                    "details": "Detailed analysis"
                }
            },
            {
                "path": "/analyze-url",
                "method": "POST",
                "description": "Analyze a news article from a URL",
                "parameters": {
                    "url": "The URL of the news article"
                },
                "response": {
                    "prediction": "REAL or FAKE",
                    "trust_score": "Trust score (0-100)",
                    "article": "Extracted article content"
                }
            },
            {
                "path": "/extract-url",
                "method": "POST",
                "description": "Extract content from a URL",
                "parameters": {
                    "url": "The URL to extract content from"
                },
                "response": {
                    "title": "Article title",
                    "content": "Article content",
                    "source": "Source domain",
                    "source_credibility": "Source credibility score"
                }
            },
            {
                "path": "/feedback",
                "method": "POST",
                "description": "Submit feedback for a misclassified article",
                "parameters": {
                    "text": "The content of the news article",
                    "predicted_label": "The label predicted by the model (0=FAKE, 1=REAL)",
                    "corrected_label": "The corrected label provided by the user",
                    "source": "Source of the feedback (optional)"
                },
                "response": {
                    "success": "Whether the feedback was saved successfully"
                }
            },
            {
                "path": "/model-info",
                "method": "GET",
                "description": "Get information about the currently loaded model",
                "response": {
                    "source": "Source of the model (mlflow or local)",
                    "version": "Model version",
                    "mlops_available": "Whether MLOps integration is available"
                }
            },
            {
                "path": "/forgot-password",
                "method": "POST",
                "description": "Request a password reset",
                "parameters": {
                    "email": "The email of the user"
                },
                "response": {
                    "success": "Whether the request was successful",
                    "message": "A message describing the result"
                }
            },
            {
                "path": "/reset-password",
                "method": "POST",
                "description": "Reset a password using a reset token",
                "parameters": {
                    "token": "The reset token",
                    "new_password": "The new password"
                },
                "response": {
                    "success": "Whether the password was reset successfully",
                    "message": "A message describing the result"
                }
            }
        ],
        "models_loaded": models_loaded,
        "mlops_available": MLOPS_AVAILABLE
    }

@app.get("/model-info")
def model_info():
    """
    Get information about the currently loaded model.
    """
    info = get_model_info()
    info["models_loaded"] = models_loaded
    return info

@app.post("/feedback")
def submit_model_feedback(feedback: FeedbackInput, current_user: User = Depends(get_current_user)):
    """
    Submit feedback for a misclassified article.
    Requires authentication.
    """
    try:
        # Set the source to include the username if not specified
        source = feedback.source
        if source == "user":
            source = f"user_{current_user.username}"

        # Submit the feedback
        success = submit_feedback(
            text=feedback.text,
            predicted_label=feedback.predicted_label,
            corrected_label=feedback.corrected_label,
            source=source
        )

        if success:
            return {"success": True, "message": "Feedback submitted successfully"}
        else:
            return {"success": False, "message": "Failed to submit feedback"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-drift", status_code=202)
def trigger_drift_check(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Trigger a concept drift check.
    This is an admin-only endpoint.
    """
    # Check if the user has admin privileges (you would need to add this field to your User model)
    if not hasattr(current_user, "is_admin") or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    if not MLOPS_AVAILABLE:
        raise HTTPException(status_code=503, detail="MLOps integration not available")

    # Run the drift check in the background
    background_tasks.add_task(check_drift)

    return {"message": "Drift check triggered. Results will be saved to the drift directory."}


# Authentication endpoints

@app.post("/register", response_model=User)
def register_user(user: UserCreate):
    """
    Register a new user.
    """
    try:
        created_user = create_user(user.email, user.username, user.password)
        return User(
            id=created_user["id"],
            email=created_user["email"],
            username=created_user["username"],
            created_at=datetime.fromisoformat(created_user["created_at"]),
            last_login=None,
            is_active=created_user["is_active"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the current user.
    """
    return current_user


@app.get("/users/me/profile", response_model=UserProfile)
def read_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current user's profile.
    """
    try:
        profile = get_user_profile(current_user.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/forgot-password")
def forgot_password(request: PasswordResetRequest):
    """
    Request a password reset.
    """
    # Check if the email exists
    token = create_password_reset_token(request.email)

    if token:
        # In a real application, you would send an email with the reset link
        # For this demo, we'll just return the token
        reset_link = f"/reset-password?token={token}"
        return {
            "success": True,
            "message": "Password reset link sent to your email",
            "reset_link": reset_link  # This would normally be sent via email
        }
    else:
        # Don't reveal that the email doesn't exist for security reasons
        return {
            "success": True,
            "message": "If your email is registered, you will receive a password reset link"
        }


@app.post("/reset-password")
def reset_password_endpoint(reset: PasswordReset):
    """
    Reset a password using a reset token.
    """
    success = reset_password(reset.token, reset.new_password)

    if success:
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )


@app.get("/users/me/analyses", response_model=List[Analysis])
def read_user_analyses(current_user: User = Depends(get_current_user)):
    """
    Get the current user's analyses.
    """
    analyses = get_analyses_by_user(current_user.id)
    return [
        Analysis(
            id=a["id"],
            user_id=a["user_id"],
            content_type=a["content_type"],
            content=a["content"],
            title=a["title"],
            url=a["url"],
            prediction=a["prediction"],
            confidence=a["confidence"],
            trust_score=a["trust_score"],
            trust_level=a["trust_level"],
            created_at=datetime.fromisoformat(a["created_at"]),
            factors=a["factors"],
            details=a["details"]
        )
        for a in analyses
    ]


@app.get("/analyses/{analysis_id}", response_model=Analysis)
def read_analysis(analysis_id: str, current_user: User = Depends(get_current_user)):
    """
    Get an analysis by ID.
    """
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Check if the analysis belongs to the current user
    if analysis["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this analysis")

    return Analysis(
        id=analysis["id"],
        user_id=analysis["user_id"],
        content_type=analysis["content_type"],
        content=analysis["content"],
        title=analysis["title"],
        url=analysis["url"],
        prediction=analysis["prediction"],
        confidence=analysis["confidence"],
        trust_score=analysis["trust_score"],
        trust_level=analysis["trust_level"],
        created_at=datetime.fromisoformat(analysis["created_at"]),
        factors=analysis["factors"],
        details=analysis["details"]
    )

@app.post("/predict")
def predict(news: NewsInput):
    """
    Predict whether a news article is real or fake.
    """
    # Check if models are loaded
    if not models_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models are not loaded. The API is in limited functionality mode."
        )

    try:
        vect_text = vectorizer.transform([news.text])
        pred = classifier.predict(vect_text)[0]
        proba = classifier.predict_proba(vect_text)[0]
        confidence = proba[pred]

        return {
            "prediction": "REAL" if pred == 1 else "FAKE",
            "confidence": confidence,  # Return as decimal for frontend
            "text_length": len(news.text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import textstat
from textblob import TextBlob
from urllib.parse import urlparse
import numpy as np
import re

KNOWN_TRUSTED_DOMAINS = ["bbc.com", "reuters.com", "nytimes.com", "theguardian.com"]
KNOWN_UNTRUSTED_DOMAINS = ["theonion.com", "infowars.com", "breitbart.com"]

@app.post("/trust-score")
def get_trust_score(news: NewsInput, current_user: Optional[User] = None):
    """
    Calculate a trust score for a news article.
    Authentication is optional for this endpoint.
    """
    # Check if models are loaded
    if not models_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models are not loaded. The API is in limited functionality mode."
        )

    try:
        # Get the prediction first
        vect_text = vectorizer.transform([news.text])
        pred = classifier.predict(vect_text)[0]
        proba = classifier.predict_proba(vect_text)[0]
        confidence = proba[pred]

        # Calculate trust factors
        text = news.text.lower()

        # 1. Source credibility (based on citations and references)
        has_citations = bool(re.search(r'according to|reported by|cited|source|reference', text))
        source_credibility = 65 + (15 if has_citations else 0) + np.random.randint(-10, 10)

        # 2. Content analysis (based on text length, structure)
        word_count = len(text.split())
        readability = textstat.flesch_reading_ease(text)
        readability_normalized = min(100, max(0, readability))
        content_analysis = (40 + word_count / 20 + readability_normalized / 5) / 3 * 100
        content_analysis = min(85, content_analysis) + np.random.randint(-5, 5)

        # 3. Language analysis (check for sensationalist language)
        sensationalist_words = ['shocking', 'amazing', 'unbelievable', 'secret', 'conspiracy',
                               'miracle', 'incredible', 'never seen before', 'won\'t believe']
        sensationalism_count = sum(1 for word in sensationalist_words if word in text)

        # Sentiment neutrality (more neutral is better)
        polarity = abs(TextBlob(text).sentiment.polarity)
        language_analysis = max(30, 80 - (sensationalism_count * 10) - (polarity * 20)) + np.random.randint(-5, 5)

        # 4. Fact verification (based on prediction confidence)
        fact_verification = 50 + (confidence * 40) + np.random.randint(-10, 10)

        # Calculate overall trust score (weighted average)
        trust_score = int(round(
            source_credibility * 0.25 +
            content_analysis * 0.25 +
            language_analysis * 0.25 +
            fact_verification * 0.25
        ))

        # Ensure values are within bounds
        trust_score = max(0, min(100, trust_score))
        source_credibility = max(0, min(100, source_credibility))
        content_analysis = max(0, min(100, content_analysis))
        language_analysis = max(0, min(100, language_analysis))
        fact_verification = max(0, min(100, fact_verification))

        # Determine trust level
        trust_level = "Low Trust"
        if trust_score >= 70:
            trust_level = "High Trust"
        elif trust_score >= 50:
            trust_level = "Medium Trust"

        # Create the result
        result = {
            "score": trust_score,
            "trust_level": trust_level,
            "prediction": "REAL" if pred == 1 else "FAKE",
            "factors": {
                "source_credibility": int(source_credibility),
                "content_analysis": int(content_analysis),
                "language_analysis": int(language_analysis),
                "fact_verification": int(fact_verification)
            },
            "details": {
                "word_count": word_count,
                "has_citations": 1 if has_citations else 0,
                "sensationalism_level": sensationalism_count,
                "readability_score": round(readability, 1),
                "sentiment_polarity": round(polarity, 2),
                "prediction_confidence": round(confidence, 2)
            }
        }

        # Save the analysis if the user is authenticated
        if current_user:
            # Get a preview of the text (first 100 characters)
            text_preview = news.text[:100] + "..." if len(news.text) > 100 else news.text

            analysis = create_analysis(
                user_id=current_user.id,
                content_type="text",
                content=news.text,
                title=text_preview,
                url=None,
                prediction="REAL" if pred == 1 else "FAKE",
                confidence=float(confidence),
                trust_score=trust_score,
                trust_level=trust_level,
                factors=result["factors"],
                details=result["details"]
            )
            result["analysis_id"] = analysis["id"]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-url")
def extract_url(url_input: UrlInput):
    """
    Extract content from a URL.
    This endpoint is public and does not require authentication.
    """
    url = url_input.url

    # Validate the URL
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    # Extract the article content
    article = get_article_from_url(url)

    if not article:
        raise HTTPException(status_code=404, detail="Failed to extract content from the URL")

    # Create a response with the most important fields first
    response = {
        "title": article.get("title", ""),
        "content": article.get("content", ""),
        "source": article.get("domain", article.get("source", "")),
        "source_credibility": article.get("source_credibility", 50),
        "extraction_method": article.get("extraction_method", ""),
        "url": url,
        "is_known_fake_news": article.get("is_known_fake_news", False),
        "reading_time_minutes": article.get("reading_time_minutes", 1),
        "timestamp": article.get("timestamp", datetime.now().isoformat()),
    }

    # Add optional fields if they exist
    if article.get("summary"):
        response["summary"] = article["summary"]

    if article.get("authors"):
        response["authors"] = article["authors"]

    if article.get("publish_date"):
        response["publish_date"] = article["publish_date"]

    if article.get("description"):
        response["description"] = article["description"]

    if article.get("section"):
        response["section"] = article["section"]

    if article.get("keywords"):
        response["keywords"] = article["keywords"]

    return response


@app.post("/analyze-url")
async def analyze_url(request: Request):
    """
    Analyze a news article from a URL.
    This is a public endpoint that does not require authentication.
    """
    print("Received analyze-url request")

    # Get the raw request body for debugging
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        print(f"Raw request body: {body_str}")

        # Try to parse as JSON
        try:
            data = json.loads(body_str)
            url = data.get('url')
            print(f"Extracted URL from JSON: {url}")
        except json.JSONDecodeError:
            # If not JSON, try to parse as form data
            form_data = await request.form()
            url = form_data.get('url')
            print(f"Extracted URL from form: {url}")

        if not url:
            print("URL is missing in request")
            return JSONResponse(
                status_code=400,
                content={"detail": "URL is required"}
            )

        # Ensure URL has http:// or https:// prefix
        if not url.startswith('http://') and not url.startswith('https://'):
            url = f"https://{url}"
            print(f"Added https:// prefix: {url}")

        # Basic URL validation
        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                print(f"Invalid URL (no netloc): {url}")
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid URL format. Please include a valid domain."}
                )
        except Exception as e:
            print(f"URL parsing error: {e}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Invalid URL: {str(e)}"}
            )

    except Exception as e:
        print(f"Error processing request: {e}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Error processing request: {str(e)}"}
        )

    # Check if models are loaded
    if not models_loaded:
        print("Models not loaded")
        return JSONResponse(
            status_code=503,
            content={"detail": "Models are not loaded. The API is in limited functionality mode."}
        )

    # Extract the article content
    print(f"Fetching article from URL: {url}")
    article = get_article_from_url(url)

    if not article:
        raise HTTPException(status_code=404, detail="Failed to extract content from the URL")

    # Create a NewsInput object with the extracted content
    news_input = NewsInput(text=article["content"])

    try:
        # Get the prediction
        prediction_result = predict(news_input)

        # Get the trust score
        trust_score_result = get_trust_score(news_input)

        # Adjust trust score based on source credibility
        adjusted_trust_score = trust_score_result["score"]

        # If the source is known to be fake news, reduce the trust score
        if article.get("is_known_fake_news", False):
            adjusted_trust_score = max(0, adjusted_trust_score - 30)

        # If the source has high credibility, boost the trust score slightly
        if article.get("source_credibility", 0) > 80:
            adjusted_trust_score = min(100, adjusted_trust_score + 10)

        # Determine trust level
        trust_level = "Low Trust"
        if adjusted_trust_score >= 70:
            trust_level = "High Trust"
        elif adjusted_trust_score >= 50:
            trust_level = "Medium Trust"

        # Create article response with the most important fields first
        article_response = {
            "title": article.get("title", ""),
            "content": article.get("content", ""),
            "source": article.get("domain", article.get("source", "")),
            "source_credibility": article.get("source_credibility", 50),
            "extraction_method": article.get("extraction_method", ""),
            "url": url,
            "is_known_fake_news": article.get("is_known_fake_news", False),
            "reading_time_minutes": article.get("reading_time_minutes", 1),
            "timestamp": article.get("timestamp", datetime.now().isoformat()),
        }

        # Add optional fields if they exist
        if article.get("summary"):
            article_response["summary"] = article["summary"]

        if article.get("authors"):
            article_response["authors"] = article["authors"]

        if article.get("publish_date"):
            article_response["publish_date"] = article["publish_date"]

        if article.get("description"):
            article_response["description"] = article["description"]

        if article.get("section"):
            article_response["section"] = article["section"]

        if article.get("keywords"):
            article_response["keywords"] = article["keywords"]

        # Combine the results
        result = {
            "prediction": prediction_result["prediction"],
            "confidence": prediction_result["confidence"],
            "trust_score": adjusted_trust_score,
            "original_trust_score": trust_score_result["score"],
            "trust_level": trust_level,
            "factors": trust_score_result["factors"],
            "details": {
                **trust_score_result["details"],
                "source_credibility": article.get("source_credibility", 50),
                "is_known_fake_news": 1 if article.get("is_known_fake_news", False) else 0,
                "reading_time_minutes": article.get("reading_time_minutes", 1),
            },
            "article": article_response
        }

        # We're not handling authentication in this simplified version
        # The analysis will not be saved to a user profile

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_trust_score(text: str, model_confidence: float, url: str = None) -> float:
    trust = model_confidence * 100

    # 1. Domain-based score
    domain_score = 0
    if url:
        domain = urlparse(url).netloc.replace("www.", "")
        if domain in KNOWN_TRUSTED_DOMAINS:
            domain_score = +10
        elif domain in KNOWN_UNTRUSTED_DOMAINS:
            domain_score = -15

    # 2. Readability: the easier, the more trustworthy?
    readability = textstat.flesch_reading_ease(text)
    readability_score = (readability - 30) / 70 * 10  # Normalize to ~10 pts range

    # 3. Sentiment neutrality
    polarity = abs(TextBlob(text).sentiment.polarity)
    sentiment_score = (1 - polarity) * 10  # Closer to 0 → more neutral → better

    final_score = trust + domain_score + readability_score + sentiment_score
    return max(0, min(100, round(final_score, 2)))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic health check - can be expanded based on needs
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "api_info": {
                "title": app.title,
                "description": app.description
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
