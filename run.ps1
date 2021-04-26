param (
    [string] $tag = "test",
    [Parameter(Position=0, ValueFromRemainingArguments)] $arguments
)

$ErrorActionPreference = "Stop"

docker run -ti --rm -v ${PWD}:/data asciicast2movie:${tag} $arguments
