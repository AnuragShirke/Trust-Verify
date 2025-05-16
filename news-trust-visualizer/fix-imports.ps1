# PowerShell script to update imports in all TypeScript files

# Get all TypeScript files in the src directory
$files = Get-ChildItem -Path .\src -Recurse -Include *.ts,*.tsx

foreach ($file in $files) {
    # Read the file content
    $content = Get-Content -Path $file.FullName -Raw
    
    # Check if the file imports from @/lib/utils
    if ($content -match "import\s+{\s*cn\s*}\s+from\s+['""]@/lib/utils['""]") {
        Write-Host "Updating imports in $($file.FullName)"
        
        # Calculate relative path to utils.js
        $relativePath = "../utils.js"
        if ($file.FullName -match "src\\components\\ui\\") {
            $relativePath = "../../../utils.js"
        } elseif ($file.FullName -match "src\\components\\") {
            $relativePath = "../utils.js"
        } elseif ($file.FullName -match "src\\pages\\") {
            $relativePath = "../utils.js"
        }
        
        # Replace the import statement
        $newContent = $content -replace "import\s+{\s*cn\s*}\s+from\s+['""]@/lib/utils['""];?", "import { cn } from `"$relativePath`";"
        
        # Write the updated content back to the file
        Set-Content -Path $file.FullName -Value $newContent
    }
}

Write-Host "Import updates completed!"
