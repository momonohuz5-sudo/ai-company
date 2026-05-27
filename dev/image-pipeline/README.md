# ComfyUI Image Production Pipeline

A general-purpose AI image production pipeline tool that integrates with ComfyUI for managing artwork creation from planning through final packaging, with strict privacy controls for sensitive content.

## Features

- **Work-based Organization**: Manage multiple projects with independent configurations
- **Modular Prompt System**: Separate prompts into quality, character, setting, lighting, and camera blocks
- **Privacy-First Design**: Private/sensitive content managed separately with OPAQUE references
- **ComfyUI Integration**: REST API integration with dry-run mode for testing
- **Batch Generation**: Submit multiple scenes to ComfyUI efficiently
- **Approval Workflow**: Human-in-the-loop image selection and approval
- **Automated Packaging**: Sequential renumbering, sample separation, and ZIP creation
- **Compliance Tools**: Generate review checklists for distribution readiness
- **Windows Compatible**: Fully compatible with Windows file systems and paths

## Privacy & Safety Design

### Critical Principles

This tool is designed to **NEVER** access private or sensitive prompt content:

- **OPAQUE References**: Private/negative blocks are referenced by ID only
- **No Content Access**: Tool validates file existence but never reads private content
- **Privacy-Safe Logging**: Logs show block IDs, seeds, and paths only (never content)
- **Git Protection**: `.gitignore` prevents accidental commits of private data
- **Manual Management**: Users create/edit private blocks manually outside the tool

### How Privacy Works

1. Tool creates a private block reference with unique ID
2. User manually creates/edits `data/private/blocks/{id}.json` with actual content
3. Tool validates file exists (no content read)
4. ComfyUI reads private blocks directly during generation (outside tool scope)
5. Logs and metadata contain only block IDs, never content

## Installation

### Prerequisites

- Python 3.8 or higher
- ComfyUI instance (for actual generation)
- Windows, Linux, or macOS

### Setup

1. **Clone or navigate to the pipeline directory:**
   ```bash
   cd dev/image-pipeline
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy example configuration:**
   ```bash
   cp config/settings.example.yaml config/settings.yaml
   ```

4. **Edit configuration:**
   ```bash
   # Edit config/settings.yaml with your ComfyUI endpoint and preferences
   ```

## Configuration

Edit `config/settings.yaml`:

```yaml
comfyui:
  endpoint: "http://localhost:8188"  # Your ComfyUI API endpoint
  dry_run: true                      # Set to false for actual generation

paths:
  data_dir: "data"
  output_dir: "output"
  logs_dir: "logs"
  private_dir: "data/private"

generation:
  default_seed_start: 1000
  seed_increment: 1

packaging:
  renumber_start: 1
  sample_count: 5
  create_zip: true
```

## Quick Start

### 1. Create a Work

```bash
python -m src.cli work create my_work_001 --title "Sunset Beach Series" --description "Beach scenes at sunset"
```

### 2. Create Prompt Blocks

**Quality block (with generation parameters):**
```bash
python -m src.cli block create \
  --type quality \
  --content "masterpiece, best quality, highres, 4k" \
  --parameters '{"steps": 30, "cfg_scale": 7.5, "sampler": "euler_a", "width": 1024, "height": 1536}' \
  --id quality_hd
```

**Character block:**
```bash
python -m src.cli block create \
  --type character \
  --content "1girl, long hair, blue eyes, white dress" \
  --tags "female,adult,casual" \
  --id char_girl_001
```

**Setting block:**
```bash
python -m src.cli block create \
  --type setting \
  --content "beach, ocean, palm trees, tropical" \
  --id setting_beach
```

**Lighting block:**
```bash
python -m src.cli block create \
  --type lighting \
  --content "sunset, golden hour, warm light, soft shadows" \
  --id lighting_sunset
```

**Camera block:**
```bash
python -m src.cli block create \
  --type camera \
  --content "wide shot, full body, dynamic angle" \
  --id camera_wide
```

### 3. Create Private Block References

```bash
python -m src.cli block create-private-ref --type private --id private_001
python -m src.cli block create-private-ref --type negative --id negative_001
```

**IMPORTANT:** After creating private references, manually create the JSON files:

`data/private/blocks/private_001.json`:
```json
{
  "content": "(Your private/sensitive prompt content here)",
  "tags": []
}
```

`data/private/blocks/negative_001.json`:
```json
{
  "content": "(Your negative prompt content here)",
  "tags": []
}
```

### 4. Create Scene Plan

Create `scenes_config.json`:
```json
[
  {
    "scene_no": 1,
    "quality_id": "quality_hd",
    "character_id": "char_girl_001",
    "setting_id": "setting_beach",
    "lighting_id": "lighting_sunset",
    "camera_id": "camera_wide",
    "private_id": "private_001",
    "negative_id": "negative_001",
    "seed": 1000
  },
  {
    "scene_no": 2,
    "quality_id": "quality_hd",
    "character_id": "char_girl_001",
    "setting_id": "setting_beach",
    "lighting_id": "lighting_sunset",
    "camera_id": "camera_wide",
    "private_id": "private_001",
    "negative_id": "negative_001",
    "seed": 1001
  }
]
```

Generate plan:
```bash
python -m src.cli scene plan my_work_001 --config-file scenes_config.json
```

### 5. Submit to ComfyUI (Dry-Run)

```bash
python -m src.cli generate submit my_work_001 --dry-run
```

**Note:** Dry-run mode logs what would happen without making actual API calls.

### 6. Submit to ComfyUI (Production)

Edit `config/settings.yaml` and set `dry_run: false`, then:

```bash
python -m src.cli generate submit my_work_001
```

### 7. Approve Images

After generation completes and images are organized:

```bash
python -m src.cli approve my_work_001 output/my_work_001/raw/scene_001/image_0001.png
python -m src.cli approve my_work_001 output/my_work_001/raw/scene_001/image_0002.png
# ... approve more images
```

### 8. Package for Distribution

```bash
python -m src.cli package my_work_001
```

This will:
- Renumber approved images sequentially (001.png, 002.png, ...)
- Separate sample images from sales images
- Export metadata.json
- Create `work_my_work_001.zip`

### 9. Generate Compliance Checklist

```bash
python -m src.cli compliance my_work_001
```

Review the checklist at `output/my_work_001/compliance_checklist.md` and ensure all items are verified before distribution.

## Command Reference

### Work Management

```bash
# Create a new work
python -m src.cli work create <work_id> --title "Title" --description "Description"

# List all works
python -m src.cli work list

# Show work details
python -m src.cli work show <work_id>
```

### Prompt Block Management

```bash
# Create a general block
python -m src.cli block create --type <type> --content "..." [--parameters '{}'] [--tags "tag1,tag2"]

# Create private block reference (OPAQUE)
python -m src.cli block create-private-ref --type <private|negative> [--id <custom_id>]

# List blocks by type
python -m src.cli block list --type <type>
```

### Scene Planning

```bash
# Create scene plan from config file
python -m src.cli scene plan <work_id> --config-file scenes.json

# Export scene plan
python -m src.cli scene export <work_id> [--format csv|jsonl]
```

### Generation

```bash
# Submit batch to ComfyUI
python -m src.cli generate submit <work_id> [--dry-run]
```

### Approval

```bash
# Mark image as approved
python -m src.cli approve <work_id> <image_path>
```

### Packaging

```bash
# Package approved images
python -m src.cli package <work_id>
```

### Compliance

```bash
# Generate compliance checklist
python -m src.cli compliance <work_id>
```

## Directory Structure

```
dev/image-pipeline/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   ├── settings.yaml           # User configuration (not committed)
│   └── settings.example.yaml   # Template
├── src/                        # Source code
├── tests/                      # Unit tests
├── data/                       # NOT committed
│   ├── works/                  # Work definitions
│   ├── blocks/                 # General prompt blocks
│   │   ├── quality/
│   │   ├── character/
│   │   ├── setting/
│   │   ├── lighting/
│   │   └── camera/
│   ├── private/                # PRIVATE (gitignored)
│   │   └── blocks/             # Private/negative blocks
│   └── scenes/                 # Scene plans
├── output/                     # NOT committed
│   └── {work_id}/
│       ├── raw/                # ComfyUI outputs by scene
│       ├── approved/           # Approved images
│       ├── rejected/           # Rejected images
│       └── package/            # Final packaged outputs
└── logs/                       # Privacy-safe logs
```

## Private Block Management

### Creating Private Blocks

1. **Create reference via CLI:**
   ```bash
   python -m src.cli block create-private-ref --type private --id private_001
   ```

2. **Manually create JSON file:**
   `data/private/blocks/private_001.json`:
   ```json
   {
     "content": "(Your actual private prompt content)",
     "tags": ["tag1", "tag2"]
   }
   ```

3. **Tool validates existence only** (never reads content)

### Privacy Guarantees

- Tool NEVER reads private block content
- Logs show only block IDs (e.g., `private_001`), never content
- Error messages sanitized to exclude private data
- Metadata exports mark private blocks as `"OPAQUE"`
- `.gitignore` prevents accidental git commits

## Troubleshooting

### "Work not found" Error

Ensure the work was created with `work create` before using it in other commands.

### "Block not found" Error

Verify:
1. General blocks exist: `python -m src.cli block list --type <type>`
2. Private block marker files exist: `ls data/private/blocks/`
3. Block IDs in scene config match created blocks

### ComfyUI Connection Failed

1. Verify ComfyUI is running
2. Check `endpoint` in `config/settings.yaml`
3. Test with `--dry-run` first

### No Images in Package

1. Ensure images were approved: `ls output/<work_id>/approved/`
2. Check that `package` command was run after approval

### Private Content in Logs

**This should NEVER happen.** If you see private content in logs:
1. Stop using the tool immediately
2. Report the issue with steps to reproduce
3. Check that you're using the official version

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Features

1. Follow privacy-first design principles
2. Never access `data/private/` directory
3. Log block IDs only, never content
4. Add unit tests with privacy validation

## License

(Add your license here)

## Support

For issues, questions, or contributions:
- GitHub Issues: (Add repository URL)
- Documentation: This README

## Important Reminder

**This tool is designed to assist with artwork production while maintaining strict privacy boundaries. Always:**

1. Review final outputs manually before distribution
2. Complete the compliance checklist
3. Verify platform-specific requirements
4. Ensure all content meets legal and ethical standards
5. Keep private blocks secure and never commit to version control
