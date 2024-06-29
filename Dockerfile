FROM gitpod/openvscode-server:latest

ENV OPENVSCODE_SERVER_ROOT="/home/.openvscode-server"
ENV OPENVSCODE="${OPENVSCODE_SERVER_ROOT}/bin/openvscode-server"


# Install dependencies
RUN sudo apt-get update \
    && sudo apt-get install -y --no-install-recommends \
        xvfb x11vnc fluxbox dbus-x11 x11-utils x11-xserver-utils xdg-utils \
        fbautostart xterm eterm gnome-terminal gnome-keyring seahorse nautilus \
        libx11-dev libxkbfile-dev libsecret-1-dev libnotify4 libnss3 libxss1 \
        libasound2 libgbm1 xfonts-base xfonts-terminus fonts-noto fonts-wqy-microhei \
        fonts-droid-fallback vim-tiny nano libgconf2-dev libgtk-3-dev twm openjdk-21-jdk python3 nodejs npm\
    && sudo apt-get clean && sudo rm -rf /var/cache/apt/* && sudo rm -rf /var/lib/apt/lists/* && sudo rm -rf /tmp/*

ENV DISABLE_V8_COMPILE_CACHE=1

SHELL ["/bin/bash", "-c"]
RUN \
    # Direct download links to external .vsix not available on https://open-vsx.org/
    # The two links here are just used as example, they are actually available on https://open-vsx.org/
    urls=(\
        https://open-vsx.org/api/redhat/java/linux-arm64/1.33.2024062908/file/redhat.java-1.33.2024062908@linux-arm64.vsix \
        https://open-vsx.org/api/ms-python/python/2024.4.1/file/ms-python.python-2024.4.1.vsix \
        https://open-vsx.org/api/genuitecllc/codetogether/2024.3.0/file/genuitecllc.codetogether-2024.3.0.vsix \
    )\
    # Create a tmp dir for downloading
    && tdir=/tmp/exts && mkdir -p "${tdir}" && cd "${tdir}" \
    # Download via wget from $urls array.
    && wget "${urls[@]}" && \
    # List the extensions in this array
    exts=(\
        # From https://open-vsx.org/ registry directly
        gitpod.gitpod-theme \
        # From filesystem, .vsix that we downloaded (using bash wildcard '*')
        "${tdir}"/* \
    )\
    # Install the $exts
    && for ext in "${exts[@]}"; do ${OPENVSCODE} --install-extension "${ext}"; done