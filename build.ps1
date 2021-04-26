param (
    [string] $tag = "test"
)

$ErrorActionPreference = "Stop"

docker build -t asciicast2movie:${tag} -f Dockerfile .
