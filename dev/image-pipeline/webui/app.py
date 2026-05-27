"""Streamlit WebUI for ComfyUI Image Production Pipeline."""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.logger import get_logger
from src.project_manager import ProjectManager
from src.prompt_manager import PromptManager
from src.scene_planner import ScenePlanner
from src.workflow_manager import WorkflowManager
from src.comfyui_client import ComfyUIClient
from src.approval import ApprovalManager
from src.packager import Packager
from src.storage import Storage


# Page config
st.set_page_config(
    page_title="ComfyUI Image Production Pipeline",
    page_icon="🎨",
    layout="wide"
)

# Initialize session state
if "initialized" not in st.session_state:
    root_dir = Path(__file__).parent.parent
    config_path = root_dir / "config" / "settings.yaml"

    if not config_path.exists():
        config_path = None

    st.session_state.config = load_config(config_path, root_dir)
    st.session_state.logger = get_logger("webui", st.session_state.config.logs_dir)
    st.session_state.initialized = True

config = st.session_state.config
logger = st.session_state.logger

# Sidebar
st.sidebar.title("🎨 Image Pipeline")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "ナビゲーション",
    ["🏠 ホーム", "📁 作品管理", "✏️ ブロック管理", "🎬 シーン計画", "🚀 生成実行", "✅ 採用管理", "📦 パッケージング"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 設定")
st.sidebar.text(f"Endpoint: {config.comfyui_endpoint}")
st.sidebar.text(f"Dry-run: {'ON' if config.dry_run else 'OFF'}")

# Initialize managers
pm_proj = ProjectManager(config.get_work_dir("").parent, logger)
pm_prompt = PromptManager(config.data_dir / "blocks", config.private_dir, logger)
sp = ScenePlanner(
    config.get_scenes_dir(),
    config.output_dir,
    pm_prompt,
    logger,
    config.default_seed_start,
    config.seed_increment
)
wm = WorkflowManager(Path(__file__).parent.parent / "workflows", logger)
comfy = ComfyUIClient(
    config.comfyui_endpoint,
    config.comfyui_timeout,
    config.dry_run,
    logger
)
am = ApprovalManager(config.output_dir, logger)
packager = Packager(config.output_dir, logger)

# Pages
if page == "🏠 ホーム":
    st.title("🎨 ComfyUI Image Production Pipeline")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("作品数", len(pm_proj.list_works()))

    with col2:
        quality_blocks = pm_prompt.list_blocks("quality")
        st.metric("プロンプトブロック", len(quality_blocks))

    with col3:
        st.metric("接続状態", "OK" if comfy.check_connection() else "NG")

    st.markdown("---")

    st.markdown("### 🚀 クイックスタート")
    st.markdown("""
    1. **作品管理** で新しい作品を作成
    2. **ブロック管理** でプロンプトブロックを作成
    3. **シーン計画** でシーンを計画
    4. **生成実行** でComfyUIに送信
    5. **採用管理** で画像を選択
    6. **パッケージング** で最終出力
    """)

    st.markdown("---")

    st.markdown("### 📚 ドキュメント")
    st.markdown("""
    - [README](../README.md)
    - [QUICKSTART](../QUICKSTART.md)
    - [HOW_IT_WORKS](../HOW_IT_WORKS.md)
    """)

elif page == "📁 作品管理":
    st.title("📁 作品管理")
    st.markdown("---")

    tab1, tab2 = st.tabs(["作品一覧", "新規作成"])

    with tab1:
        st.subheader("作品一覧")
        works = pm_proj.list_works()

        if not works:
            st.info("作品がありません。新規作成タブから作成してください。")
        else:
            for work in works:
                with st.expander(f"📁 {work.title} ({work.work_id})"):
                    st.text(f"Work ID: {work.work_id}")
                    st.text(f"タイトル: {work.title}")
                    st.text(f"説明: {work.description}")
                    st.text(f"ステータス: {work.status}")
                    st.text(f"作成日: {work.created_at}")

    with tab2:
        st.subheader("新規作成")

        with st.form("create_work"):
            work_id = st.text_input("Work ID", placeholder="work_001")
            title = st.text_input("タイトル", placeholder="Sunset Beach Series")
            description = st.text_area("説明", placeholder="Beach scenes at sunset")

            submitted = st.form_submit_button("作成")

            if submitted:
                if not work_id or not title:
                    st.error("Work IDとタイトルは必須です")
                elif pm_proj.work_exists(work_id):
                    st.error(f"Work ID '{work_id}' は既に存在します")
                else:
                    try:
                        work = pm_proj.create_work(work_id, title, description)
                        st.success(f"✓ 作品を作成しました: {work.title}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"エラー: {e}")

elif page == "✏️ ブロック管理":
    st.title("✏️ プロンプトブロック管理")
    st.markdown("---")

    tab1, tab2 = st.tabs(["ブロック一覧", "新規作成"])

    with tab1:
        st.subheader("ブロック一覧")

        block_type = st.selectbox(
            "ブロックタイプ",
            ["quality", "character", "setting", "lighting", "camera"]
        )

        blocks = pm_prompt.list_blocks(block_type)

        if not blocks:
            st.info(f"{block_type} ブロックがありません。")
        else:
            for block in blocks:
                with st.expander(f"✏️ {block.block_id}"):
                    st.text(f"Block ID: {block.block_id}")
                    st.text(f"タイプ: {block.block_type}")
                    st.text_area(f"内容", block.content, key=f"view_{block.block_id}", disabled=True)
                    if block.parameters:
                        st.json(block.parameters)
                    if block.tags:
                        st.text(f"タグ: {', '.join(block.tags)}")

    with tab2:
        st.subheader("新規作成")

        with st.form("create_block"):
            block_type = st.selectbox(
                "ブロックタイプ",
                ["quality", "character", "setting", "lighting", "camera"]
            )

            block_id = st.text_input("Block ID (オプション)", placeholder="自動生成")
            content = st.text_area("内容", placeholder="プロンプトテキスト")

            if block_type == "quality":
                st.markdown("**生成パラメータ**")
                col1, col2 = st.columns(2)
                with col1:
                    steps = st.number_input("Steps", min_value=1, max_value=150, value=25)
                    cfg_scale = st.number_input("CFG Scale", min_value=1.0, max_value=30.0, value=7.5, step=0.5)
                with col2:
                    width = st.number_input("Width", min_value=64, max_value=2048, value=768, step=64)
                    height = st.number_input("Height", min_value=64, max_value=2048, value=1024, step=64)

                sampler = st.selectbox("Sampler", ["euler", "euler_a", "heun", "dpm_2", "dpm++_2m"])

                parameters = {
                    "steps": steps,
                    "cfg_scale": cfg_scale,
                    "sampler": sampler,
                    "width": width,
                    "height": height
                }
            else:
                parameters = {}

            tags = st.text_input("タグ (カンマ区切り)", placeholder="tag1, tag2")

            submitted = st.form_submit_button("作成")

            if submitted:
                if not content:
                    st.error("内容は必須です")
                else:
                    try:
                        tag_list = [t.strip() for t in tags.split(",")] if tags else []
                        block = pm_prompt.create_block(
                            block_type,
                            content,
                            parameters,
                            tag_list,
                            block_id if block_id else None
                        )
                        st.success(f"✓ ブロックを作成しました: {block.block_id}")
                    except Exception as e:
                        st.error(f"エラー: {e}")

elif page == "🎬 シーン計画":
    st.title("🎬 シーン計画")
    st.markdown("---")

    works = pm_proj.list_works()

    if not works:
        st.warning("作品がありません。まず作品を作成してください。")
    else:
        work_id = st.selectbox("作品を選択", [w.work_id for w in works])

        st.markdown("---")

        st.subheader("シンプル計画")

        with st.form("simple_plan"):
            scene_count = st.number_input("シーン数", min_value=1, max_value=100, value=3)

            st.markdown("**ブロック選択**")
            quality_blocks = pm_prompt.list_blocks("quality")
            character_blocks = pm_prompt.list_blocks("character")
            setting_blocks = pm_prompt.list_blocks("setting")
            lighting_blocks = pm_prompt.list_blocks("lighting")
            camera_blocks = pm_prompt.list_blocks("camera")

            col1, col2 = st.columns(2)
            with col1:
                quality_id = st.selectbox("Quality", [b.block_id for b in quality_blocks] if quality_blocks else ["なし"])
                character_id = st.selectbox("Character", [b.block_id for b in character_blocks] if character_blocks else ["なし"])
                setting_id = st.selectbox("Setting", [b.block_id for b in setting_blocks] if setting_blocks else ["なし"])

            with col2:
                lighting_id = st.selectbox("Lighting", [b.block_id for b in lighting_blocks] if lighting_blocks else ["なし"])
                camera_id = st.selectbox("Camera", [b.block_id for b in camera_blocks] if camera_blocks else ["なし"])

            private_id = st.text_input("Private ID", placeholder="private_001")
            negative_id = st.text_input("Negative ID", placeholder="negative_001")

            seed_start = st.number_input("開始Seed", min_value=0, value=1000)

            submitted = st.form_submit_button("シーン計画作成")

            if submitted:
                scenes_config = []
                for i in range(1, scene_count + 1):
                    scenes_config.append({
                        "scene_no": i,
                        "quality_id": quality_id,
                        "character_id": character_id,
                        "setting_id": setting_id,
                        "lighting_id": lighting_id,
                        "camera_id": camera_id,
                        "private_id": private_id,
                        "negative_id": negative_id,
                        "seed": seed_start + i
                    })

                try:
                    scenes = sp.create_scene_plan(work_id, scenes_config, validate_blocks=True)
                    plan_file = sp.save_plan(work_id, scenes)
                    st.success(f"✓ シーン計画を作成しました: {len(scenes)} シーン")
                    st.info(f"保存先: {plan_file}")
                except Exception as e:
                    st.error(f"エラー: {e}")

elif page == "🚀 生成実行":
    st.title("🚀 生成実行")
    st.markdown("---")

    works = pm_proj.list_works()

    if not works:
        st.warning("作品がありません。")
    else:
        work_id = st.selectbox("作品を選択", [w.work_id for w in works])

        # Check if scene plan exists
        try:
            scenes = sp.load_plan(work_id)

            st.info(f"シーン数: {len(scenes)}")

            if config.dry_run:
                st.warning("⚠️ Dry-runモードです。実際の生成は行われません。")

            if st.button("🚀 生成実行", type="primary"):
                with st.spinner("ワークフロー構築中..."):
                    workflows = []

                    for scene in scenes:
                        blocks = {
                            'quality': pm_prompt.get_block(scene.quality_id, 'quality'),
                            'character': pm_prompt.get_block(scene.character_id, 'character'),
                            'setting': pm_prompt.get_block(scene.setting_id, 'setting'),
                            'lighting': pm_prompt.get_block(scene.lighting_id, 'lighting'),
                            'camera': pm_prompt.get_block(scene.camera_id, 'camera')
                        }

                        # Load private blocks
                        private_file = config.private_dir / "blocks" / f"{scene.private_id}.json"
                        negative_file = config.private_dir / "blocks" / f"{scene.negative_id}.json"

                        private_blocks = {
                            'private': Storage.load_json(private_file) if private_file.exists() else {},
                            'negative': Storage.load_json(negative_file) if negative_file.exists() else {}
                        }

                        workflow = wm.build_workflow(scene, blocks, private_blocks)
                        workflows.append(workflow)

                st.success(f"✓ ワークフロー構築完了: {len(workflows)} シーン")

                with st.spinner("ComfyUIに送信中..."):
                    job_ids = comfy.submit_batch_with_workflows(scenes, workflows)

                success_count = sum(1 for jid in job_ids if jid)
                st.success(f"✓ 送信完了: {success_count}/{len(scenes)} シーン")

                if job_ids:
                    st.markdown("### Job IDs")
                    for i, jid in enumerate(job_ids, 1):
                        if jid:
                            st.code(f"Scene {i}: {jid}")

        except FileNotFoundError:
            st.error("シーン計画が見つかりません。先にシーン計画を作成してください。")

elif page == "✅ 採用管理":
    st.title("✅ 採用管理")
    st.markdown("---")

    works = pm_proj.list_works()

    if not works:
        st.warning("作品がありません。")
    else:
        work_id = st.selectbox("作品を選択", [w.work_id for w in works])

        # Get images
        raw_dir = config.output_dir / work_id / "raw"

        if raw_dir.exists():
            st.subheader("生成画像")

            for scene_dir in sorted(raw_dir.iterdir()):
                if scene_dir.is_dir():
                    with st.expander(f"📁 {scene_dir.name}"):
                        images = list(scene_dir.glob("*.png"))

                        if images:
                            cols = st.columns(3)
                            for idx, img_path in enumerate(images):
                                with cols[idx % 3]:
                                    st.image(str(img_path), caption=img_path.name, use_container_width=True)
                                    if st.button(f"✅ 採用", key=f"approve_{img_path}"):
                                        am.mark_approved(work_id, img_path)
                                        st.success("採用しました")
                                        st.rerun()
                        else:
                            st.info("画像がありません")
        else:
            st.info("生成画像がありません")

        st.markdown("---")
        st.subheader("採用済み画像")

        approved = am.list_approved(work_id)
        if approved:
            st.text(f"採用数: {len(approved)}")
            cols = st.columns(3)
            for idx, img_path in enumerate(approved):
                with cols[idx % 3]:
                    st.image(str(img_path), caption=img_path.name, use_container_width=True)
        else:
            st.info("採用済み画像がありません")

elif page == "📦 パッケージング":
    st.title("📦 パッケージング")
    st.markdown("---")

    works = pm_proj.list_works()

    if not works:
        st.warning("作品がありません。")
    else:
        work_id = st.selectbox("作品を選択", [w.work_id for w in works])

        approved = am.list_approved(work_id)
        st.metric("採用画像数", len(approved))

        if len(approved) == 0:
            st.warning("採用画像がありません。先に画像を採用してください。")
        else:
            if st.button("📦 パッケージ作成", type="primary"):
                with st.spinner("パッケージ作成中..."):
                    try:
                        # Renumber
                        renumbered = packager.renumber_images(work_id, config.renumber_start)
                        st.success(f"✓ 連番リネーム完了: {len(renumbered)} 枚")

                        # Separate samples
                        if config.sample_count > 0:
                            samples, sales = packager.separate_samples(work_id, config.sample_count)
                            st.success(f"✓ サンプル分離完了: {len(samples)} サンプル, {len(sales)} 販売用")

                        # Create ZIP
                        zip_path = packager.create_package(work_id)
                        st.success(f"✓ ZIP作成完了")

                        st.balloons()

                        st.markdown("### パッケージ情報")
                        st.text(f"保存先: {zip_path}")
                        st.text(f"ファイルサイズ: {zip_path.stat().st_size / 1024:.2f} KB")

                    except Exception as e:
                        st.error(f"エラー: {e}")
