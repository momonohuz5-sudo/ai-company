# CLAUDE.md - Image Pipeline Tool Guidance

This file provides guidance to Claude Code when working with the ComfyUI Image Production Pipeline tool.

## Tool Overview

This is a **privacy-first** image production pipeline tool that integrates with ComfyUI. It manages artwork creation from planning through packaging while maintaining strict separation between general-purpose prompts and private/sensitive content.

## Privacy Principles (CRITICAL)

### What Claude Code MUST NOT Do

1. **NEVER read private block content** from `data/private/blocks/`
2. **NEVER suggest adding NSFW/adult content** to prompts
3. **NEVER generate private prompt examples** with explicit content
4. **NEVER log or display** private block content in any form
5. **NEVER propose changes** to private block files

### What Claude Code CAN Do

1. **Create private block references** (ID only, no content)
2. **Validate private block existence** (file check, no content read)
3. **Log block IDs** in privacy-safe manner
4. **Suggest general prompt improvements** (quality, composition, lighting)
5. **Help with workflow** and tool usage

### Privacy-Safe Operations

```python
# ✓ GOOD: Check if private block exists
prompt_manager.validate_block_exists("private_001", "private")

# ✓ GOOD: Create private reference
ref = prompt_manager.create_private_ref("private", "private_001")

# ✗ BAD: Read private block content
# DON'T DO THIS - NEVER ACCESS data/private/blocks/*.json
```

## Architecture Overview

### Core Modules

- `models.py`: Data structures (Work, PromptBlock, Scene)
- `storage.py`: JSON file operations with atomic writes
- `config.py`: YAML configuration loader
- `logger.py`: Privacy-safe logging
- `project_manager.py`: Work CRUD operations
- `prompt_manager.py`: Prompt block management (with privacy controls)
- `scene_planner.py`: Scene plan generation and validation
- `comfyui_client.py`: ComfyUI API integration with dry-run mode
- `organizer.py`: Image file organization
- `approval.py`: Approval workflow management
- `packager.py`: Renumbering and ZIP packaging
- `metadata.py`: Metadata export (privacy-safe)
- `compliance.py`: Compliance checklist generation
- `cli.py`: Command-line interface

### Data Flow

1. Work Creation → `data/works/{work_id}.json`
2. Prompt Blocks → `data/blocks/{type}/{block_id}.json`
3. Private Refs → `data/private/blocks/{block_id}.marker` (user creates actual .json)
4. Scene Plan → `data/scenes/{work_id}_scenes.jsonl`
5. ComfyUI Submission → Generation
6. Image Organization → `output/{work_id}/raw/scene_XXX/`
7. Approval → `output/{work_id}/approved/`
8. Packaging → `output/{work_id}/package/work_{work_id}.zip`

## Development Guidelines

### When Adding Features

1. **Privacy First**: Any new feature MUST respect privacy boundaries
2. **Windows Compatibility**: Use `pathlib.Path` for all file operations
3. **Atomic Writes**: Use `Storage.save_json()` for file writes
4. **Privacy-Safe Logging**: Use `logger.log_*()` methods, never raw logging
5. **Error Handling**: Sanitize error messages to exclude private content

### Testing Requirements

All new features must include:
1. Unit tests
2. Privacy validation tests (ensure no private content in logs/output)
3. Windows path compatibility tests (if file operations involved)

### Code Review Checklist

- [ ] No direct access to `data/private/` directory
- [ ] All file operations use `pathlib.Path`
- [ ] Logging uses privacy-safe methods
- [ ] Error messages sanitized
- [ ] Documentation updated
- [ ] Tests include privacy validation

## Common Tasks

### Debugging Scene Plan Errors

**User says:** "Scene validation failed: missing blocks"

**Response:**
1. Check which blocks are missing (tool will log block IDs)
2. For general blocks: Verify with `python -m src.cli block list --type <type>`
3. For private blocks: Check if marker files exist (file check only, no content read)
4. Suggest re-creating missing block references

**Do NOT:**
- Read private block content to "debug"
- Suggest specific private prompt content

### Improving Generation Quality

**User says:** "How can I improve image quality?"

**Response:**
1. Suggest quality block parameter adjustments (steps, cfg_scale, sampler)
2. Suggest general prompt improvements (composition, lighting, camera)
3. Recommend character/setting block refinements
4. Point to ComfyUI workflow optimization resources

**Do NOT:**
- Suggest NSFW-specific improvements
- Generate example private prompts

### Workflow Optimization

**User says:** "This workflow is slow, how can I speed it up?"

**Response:**
1. Suggest batch size optimization in scene planning
2. Recommend parallel processing (if ComfyUI supports it)
3. Suggest scene plan template expansion for common variations
4. Point to dry-run mode for testing configurations

## Error Handling

### Privacy-Safe Error Messages

```python
# ✓ GOOD
raise ValueError(f"Block {block_id} validation failed")

# ✗ BAD - Exposes content
raise ValueError(f"Block {block_id} has invalid content: {content}")
```

### Common Error Scenarios

1. **Missing private block marker**: User forgot to create marker file
   - Solution: Re-run `block create-private-ref`

2. **Missing private block JSON**: User created marker but not actual JSON
   - Solution: Remind user to manually create `data/private/blocks/{id}.json`

3. **ComfyUI connection failed**: Endpoint misconfigured or ComfyUI not running
   - Solution: Check `config/settings.yaml` endpoint and ComfyUI status

## Logging Best Practices

### What to Log

- Work IDs, scene numbers
- Block IDs (OPAQUE for private)
- Seeds, file paths
- Operation success/failure
- Job IDs, timestamps

### What NOT to Log

- Prompt content (especially private)
- Image data or metadata
- User credentials
- ComfyUI API keys

## Integration Points

### ComfyUI API

The tool submits scenes to ComfyUI via REST API. The `comfyui_client.py` module:
- Builds payload with block IDs
- ComfyUI reads actual block content from disk (outside tool scope)
- Tool never accesses private block content

### Future Enhancements

When proposing or implementing new features:
1. **Always** maintain privacy boundaries
2. **Never** expand scope to include private content access
3. **Consider** Windows compatibility
4. **Document** privacy implications
5. **Test** with privacy validation suite

## Compliance & Distribution

### Pre-Distribution Checklist

Before packaging for distribution, users must:
1. Review all images manually
2. Complete compliance checklist
3. Verify platform-specific requirements
4. Ensure no private content in metadata

### Claude Code's Role

- Generate compliance checklist template
- Export metadata (privacy-safe)
- Package approved images
- **NOT**: Make judgments about content appropriateness

## Summary

This tool is a **general-purpose** image production pipeline. Claude Code assists with:
- Workflow management and automation
- General prompt optimization
- Technical troubleshooting
- Documentation and guidance

Claude Code does **NOT**:
- Access or generate private/sensitive content
- Make NSFW-specific suggestions
- Bypass privacy safeguards
- Judge content appropriateness

When in doubt, prioritize privacy and defer to the user for content decisions.
