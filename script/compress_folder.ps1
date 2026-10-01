Get-ChildItem -Path .\* -Exclude *.zip | Compress-Archive -DestinationPath research_full.zip -Force
