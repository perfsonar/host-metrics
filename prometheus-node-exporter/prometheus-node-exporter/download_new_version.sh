#!/bin/bash

VERSION="1.6.1"

TEMPDIR=$(mktemp -d)
WORKDIR=$(dirname $0)
BINDIR="${WORKDIR}/bin"

echo "Temp directory: $TEMPDIR"
echo

ARCHS=( amd64 arm64 armv7 ppc64le )
for arch in "${ARCHS[@]}"
do
  echo "[ARCH ${arch}]"
  pushd $TEMPDIR
  SRCDIR="node_exporter-${VERSION}.linux-${arch}"
  TARBALL="${SRCDIR}.tar.gz"
  URL="https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/${TARBALL}"
  echo "Fetching ${URL}..."
  curl -L -o ${TARBALL} ${URL}
  echo "Expanding  ${TARBALL}..."
  tar -xzf ${TARBALL}
  popd
  echo "Copying binary..."
  cp -f ${TEMPDIR}/${SRCDIR}/node_exporter ${BINDIR}/node_exporter.${arch}
  echo "[DONE]"
  echo ""
done

echo "[Final cleanup]"
mv -f ${BINDIR}/node_exporter.amd64 ${BINDIR}/node_exporter.x86_64 
mv -f ${BINDIR}/node_exporter.arm64 ${BINDIR}/node_exporter.aarch64
echo "[DONE]"
echo ""

