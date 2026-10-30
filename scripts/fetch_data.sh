#!/usr/bin/env bash
# Fetch the public FlyWire v783 inputs into data/raw (about 200 MB).
# Both sources are plain GitHub repositories; no account or token needed.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw
tmp="$(mktemp -d)"
git clone --depth 1 https://github.com/philshiu/Drosophila_brain_model.git "$tmp/shiu"
git clone --depth 1 https://github.com/flyconnectome/flywire_annotations.git "$tmp/ann"
cp "$tmp/shiu/Completeness_783.csv" "$tmp/shiu/Connectivity_783.parquet" "$tmp/shiu/sez_neurons.pickle" data/raw/
cp "$tmp/ann/supplemental_files/Supplemental_file1_neuron_annotations.tsv" data/raw/
rm -rf "$tmp"
echo "data/raw ready:"; ls -la data/raw
