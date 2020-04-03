# kylin local path
BASE_DIR=${1-/media/wq/xj-3t/KYLIN-ALL}
echo "BASE_DIR=${BASE_DIR}"
mkdir -p  ${BASE_DIR}

function downDir() {
	mypath=$1
	echo "mypath=${mypath}"
	FPATH=${BASE_DIR}/${mypath}

	if [ ! -f "${FPATH}/Packages" ]; then
		mkdir -p  ${FPATH}
		wget -O ${FPATH}/Packages http://archive.kylinos.cn/kylin/KYLIN-ALL/${mypath}/Packages
		wget -O ${FPATH}/Packages.gz http://archive.kylinos.cn/kylin/KYLIN-ALL/${mypath}/Packages.gz
		wget -O ${FPATH}/Packages.bz2 http://archive.kylinos.cn/kylin/KYLIN-ALL/${mypath}/Packages.bz2
	fi

	#python download.py ${BASE_DIR} ${FPATH}/Packages 50
}

dirs=(4.0.2-desktop \
4.0.2sp1-desktop \
#4.0.2sp1 4.0.2sp2-desktop \
#4.0.2sp3-desktop \
#4.0.2 \
#4.0.2sp2 \
#4.0.2sp3 \
#4.0.2-server 4.0.2sp1-server 4.0.2sp2-server-ft2000 4.0.2sp2-server 4.0.2sp3-server 10.0 \
)

for idir in ${dirs[@]}; do
	paths=(dists/${idir}/main/binary-arm64 dists/${idir}/main/binary-amd64 \
	dists/${idir}/multiverse/binary-arm64 dists/${idir}/multiverse/binary-amd64 \
	dists/${idir}/restricted/binary-arm64 dists/${idir}/restricted/binary-amd64 \
	dists/${idir}/universe/binary-arm64 dists/${idir}/universe/binary-amd64 \
	)
	for ipath in ${paths[@]}; do
  		downDir $ipath
	done
done