all:build-image

build-image:
	podman manifest rm open-gov-puller:latest
	podman build --jobs=2 --platform=linux/amd64,linux/arm64 --manifest open-gov-puller:latest .