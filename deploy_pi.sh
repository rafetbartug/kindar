#!/usr/bin/env bash
set -euo pipefail

PI_USER="rbb"
PI_HOST="172.20.10.4"
PI_PATH="/home/rbb/kindar"

echo "Deploying to Raspberry Pi at ${PI_HOST}..."

ssh "${PI_USER}@${PI_HOST}" "mkdir -p \
${PI_PATH} \
${PI_PATH}/core \
${PI_PATH}/core/storage \
${PI_PATH}/core/documents \
${PI_PATH}/ui \
${PI_PATH}/storage \
${PI_PATH}/state \
${PI_PATH}/display \
${PI_PATH}/library"

scp main.py "${PI_USER}@${PI_HOST}:${PI_PATH}/"

scp core/reader.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/session.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/reader_controller.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/recovery.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/render_reporter.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/path_policy.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/cache_manager.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/logging_config.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/config.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"
scp core/memory_profiler.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/"

scp core/documents/base.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/documents/"
scp core/documents/pdf_document.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/documents/"
scp core/documents/cbz_document.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/documents/"
scp core/documents/factory.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/documents/"


scp ui/menu.py "${PI_USER}@${PI_HOST}:${PI_PATH}/ui/"
scp storage/state_manager.py "${PI_USER}@${PI_HOST}:${PI_PATH}/storage/"
scp core/storage/crash_state_manager.py "${PI_USER}@${PI_HOST}:${PI_PATH}/core/storage/"

scp display/base.py "${PI_USER}@${PI_HOST}:${PI_PATH}/display/"
scp display/terminal_display.py "${PI_USER}@${PI_HOST}:${PI_PATH}/display/"
scp display/preview_display.py "${PI_USER}@${PI_HOST}:${PI_PATH}/display/"
scp display/eink_display.py "${PI_USER}@${PI_HOST}:${PI_PATH}/display/"
scp library/catalog.py "${PI_USER}@${PI_HOST}:${PI_PATH}/library/"

echo "Running remote smoke test..."
ssh "${PI_USER}@${PI_HOST}" "cd ${PI_PATH} && python3 -m py_compile \
main.py \
core/reader.py \
core/session.py \
core/reader_controller.py \
core/recovery.py \
core/render_reporter.py \
core/documents/base.py \
core/path_policy.py \
core/cache_manager.py \
core/logging_config.py \
core/config.py \
core/memory_profiler.py \
core/documents/pdf_document.py \
core/documents/cbz_document.py \
core/documents/factory.py \
ui/menu.py \
storage/state_manager.py \
core/storage/crash_state_manager.py \
display/base.py \
display/terminal_display.py \
display/preview_display.py \
display/eink_display.py \
library/catalog.py"

echo "Cleaning up __pycache__ on Raspberry Pi..."
ssh "${PI_USER}@${PI_HOST}" "cd ${PI_PATH} && find . -name '__pycache__' -type d -exec rm -rf {} +"

echo "Smoke test passed."

echo "Deployment to Raspberry Pi at ${PI_HOST} completed successfully."
echo "To run the application on the Raspberry Pi, use the following commands:"
echo "ssh ${PI_USER}@${PI_HOST}"
echo "cd ${PI_PATH} && python3 main.py"