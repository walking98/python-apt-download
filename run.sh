# kylin local path

BASE_DIR=/media/wq/xj-3t/KYLIN-ALL
#MY_PATH=dists/4.0.2sp2-desktop/main/binary-amd64
MY_PATH=dists/4.0.2sp2-desktop/main/binary-arm64
FPATH=${BASE_DIR}/${MY_PATH}

if [ ! -f "${FPATH}/Packages" ]; then
	mkdir -p  ${FPATH}
	wget -O ${FPATH}/Packages http://archive.kylinos.cn/kylin/KYLIN-ALL/${MY_PATH}/Packages
fi

python download.py ${BASE_DIR} ${FPATH}/Packages 50
