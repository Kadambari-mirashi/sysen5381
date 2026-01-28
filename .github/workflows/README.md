# Canvas Assignment Sync Workflow

This GitHub Actions workflow automatically syncs changed ACTIVITY, LAB, HOMEWORK, and TOOL markdown files to Canvas when you push to the `main` branch.

## How It Works

1. **Triggers**: Runs automatically on push to `main` branch when `.md` files are changed
2. **Detection**: Identifies changed files matching patterns:
   - `ACTIVITY_*.md`
   - `LAB_*.md`
   - `HOMEWORK*.md`
   - `TOOL*.md`
3. **Filtering**: Only syncs files that have a `github_path` mapping in `canvastest/assignments_metadata.json`
4. **Syncing**: Updates Canvas assignment descriptions using the `canvastest` submodule

## Setup

### 1. Required GitHub Secrets

You must configure the following secrets in your GitHub repository settings:

1. **`CANVAS_API_KEY`**
   - Your Canvas API authentication token
   - Get it from: Canvas → Account → Settings → New Access Token
   - **Important**: Never commit this key to the repository

2. **`CANVAS_COURSE_ID`**
   - Your Canvas course ID (integer)
   - Found in the Canvas course URL: `https://canvas.cornell.edu/courses/COURSE_ID`
   - Example: If URL is `https://canvas.cornell.edu/courses/81764`, the ID is `81764`

#### How to Add Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact names above

### 2. Submodule Setup

The workflow requires the `canvastest` submodule to be initialized:

```bash
git submodule update --init --recursive
```

### 3. Assignments Metadata File

The workflow requires `canvastest/assignments_metadata.json` to exist with `github_path` mappings for each assignment you want to sync.

#### Creating the Metadata File

If you don't have `assignments_metadata.json` yet:

1. Run the fetch script locally (see [canvastest README](../canvastest/README.md))
2. Edit the file to add `github_path` entries for each assignment
3. Commit the file to your repository

Example entry:

```json
{
  "id": 123456,
  "name": "Install Git and Git Bash",
  "points_possible": 10,
  "github_path": "00_quickstart/ACTIVITY_git.md"
}
```

**Important**: Only files with `github_path` entries will be synced. Files without mappings will be skipped.

## Workflow Behavior

### What Gets Synced

- Only files that:
  1. Match the assignment patterns (ACTIVITY_, LAB_, HOMEWORK*, TOOL*)
  2. Were changed in the push
  3. Have a `github_path` mapping in `assignments_metadata.json`

### What Gets Skipped

- Files that don't match assignment patterns
- Files without `github_path` mappings
- Non-markdown files

### Error Handling

- If a single file fails to sync, the workflow logs the error and continues with other files
- The workflow fails only if critical setup fails (R installation, submodule checkout)
- Check workflow logs for detailed error messages

## Workflow Logs

After pushing to `main`, you can view workflow runs:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select the **Canvas Assignment Sync** workflow
4. Click on a run to see detailed logs

## Troubleshooting

### Workflow doesn't run

- **Check**: Did you push to `main` branch?
- **Check**: Did you change any `.md` files?
- **Check**: Is the workflow file in `.github/workflows/canvas-sync.yml`?

### "No changed assignment files found"

- This is normal if you didn't change any ACTIVITY/LAB/HOMEWORK/TOOL files
- The workflow will skip syncing

### "assignments_metadata.json not found"

- **Solution**: Create `canvastest/assignments_metadata.json` with at least an empty array `[]`
- Or run the fetch script to generate it (see canvastest documentation)

### "No assignment found with github_path"

- **Cause**: The changed file doesn't have a `github_path` entry in `assignments_metadata.json`
- **Solution**: Add the `github_path` mapping for that file in the metadata file
- The workflow will skip files without mappings (this is expected behavior)

### "CANVAS_API_KEY not found"

- **Cause**: Secret not configured or incorrectly named
- **Solution**: Verify the secret is named exactly `CANVAS_API_KEY` in repository settings

### "Failed to sync" errors

- Check the workflow logs for specific error messages
- Common causes:
  - Invalid Canvas API key
  - Network issues
  - Canvas API rate limits (workflow will retry automatically)
  - Invalid markdown content

### Submodule issues

- **Error**: "Cannot find canvastest/R directory"
- **Solution**: Ensure submodule is initialized:
  ```bash
  git submodule update --init --recursive
  ```

## Security Notes

Since this is a **public repository**:

- ✅ **Secrets are secure**: GitHub Actions secrets are never exposed in logs or code
- ✅ **Workflow is visible**: Anyone can see the workflow file (this is fine - no secrets in it)
- ⚠️ **Be careful**: Never log or echo secrets in workflow steps
- ⚠️ **Check logs**: Ensure R scripts don't accidentally print API keys

The workflow automatically masks secrets in logs. The `.env` file created during workflow execution is temporary and never committed.

## Cost

**Free!** Since this is a public repository, GitHub Actions provides unlimited free minutes. You can run this workflow as frequently as needed without any cost concerns.

## Manual Testing

To test the sync script locally:

```bash
# Create a test file with changed files
echo "00_quickstart/ACTIVITY_git.md" > test_changed.txt

# Run the sync script
cd canvastest/R
Rscript ../../scripts/sync_changed_files.R \
  ../../test_changed.txt \
  ../../course_config.json \
  ../assignments_metadata.json
```

## Related Documentation

- [canvastest Module README](../canvastest/README.md) - Detailed documentation of the sync module
- [canvastest Workflow Documentation](../canvastest/docs/WORKFLOW.md) - Step-by-step workflow procedures
- [canvastest Configuration Guide](../canvastest/docs/CONFIGURATION.md) - Configuration options

## Support

If you encounter issues:

1. Check the workflow logs in the **Actions** tab
2. Review the troubleshooting section above
3. Consult the canvastest documentation
4. Verify all secrets are configured correctly
