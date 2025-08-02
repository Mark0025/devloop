# RunPod CLI Scripts

This folder holds shell snippets or small scripts that interact with RunPod via the official CLI (`runpod`). They mirror the steps outlined in `DEV_MAN/runpod_notes.mdc` but keep commands in one place for easy reuse.

## 1. Install & Authenticate

```bash
pipx install runpod   # installs runpod CLI while isolating it from project Python deps
runpod config $RUNPOD_API_KEY
```

## 2. Launch Default Pod (Ollama)

```bash
runpod pod launch --template-id ollama/ollama \
    --gpu-count 1 \
    --disk-size 80 \
    --name devloop-ollama \
    --ports "11434:http"
```

## 3. Check Status

```bash
runpod pod status --name devloop-ollama
```

## 4. Stop Pod

```bash
runpod pod stop --name devloop-ollama
```

Feel free to add more advanced scripts (Flex workers, cost export) but keep each file small and clearly named (e.g. `flex_launch.sh`).
