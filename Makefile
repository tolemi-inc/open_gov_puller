all:build-image

build-image:
	podman manifest rm open_gov_puller:latest
	podman build --jobs=2 --platform=linux/amd64,linux/arm64 --manifest open_gov_puller:latest .