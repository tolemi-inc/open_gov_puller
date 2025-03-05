all:build-image

build-image:
	podman build  --jobs=2 --platform=linux/amd64 -t python-generic:latest-amd64 .
	podman build  --jobs=2 --platform=linux/arm64 -t python-generic:latest-arm64 .
	podman manifest rm python-generic:latest || true
	podman manifest create python-generic:latest
	podman manifest add --arch amd64 python-generic:latest python-generic:latest-amd64
	podman manifest add --arch arm64 python-generic:latest python-generic:latest-arm64