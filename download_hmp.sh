declare -A samples
while read -r a b
do
        samples[$a]=$b

done <sample_list

RAWDATA="RAWDATA_HMP"
mkdir $RAWDATA

for sample in "${!samples[@]}"
do
	
	LINK=s3://human-microbiome-project/HHS/HMASM/WGS/stool/${sample}.tar.bz2
	echo $LINK 
	aws s3 cp $LINK $RAWDATA
	tar xjf $RAWDATA/${sample}.tar.bz2 -C $RAWDATA
done
