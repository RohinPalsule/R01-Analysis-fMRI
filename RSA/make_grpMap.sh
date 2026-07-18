
EXPNAME=uh
EXPDIR=./
SLDIR=${EXPDIR}/searchlight/MNI_space/

cd ${SLDIR}

#MASKS="b_hip b_hip_dil2 b_hipPlus b_hipPlus_dil2 b_mpfc b_mpfc_dil2 b_mtlc b_mtlc_dil2"
MASKS="b_gray"
COMPS="edge_nonedge_diff"

for mask in $MASKS
do
	for comparison in $COMPS	
	do
  		fslmerge -t ${SLDIR}/prepost_sl_${comparison}_${mask}_func_grp.nii.gz ${SLDIR}/*MNI.nii.gz
  		randomise -i ${SLDIR}/prepost_sl_${comparison}_${mask}_func_grp.nii.gz -o ${SLDIR}/prepost_sl_${comparison}_${mask}_func_rndm -m /Users/rohinpalsule/fsl/pkgs/fsl-data_standard-2208.0-0/data/standard/MNI152_T1_2mm_brain.nii.gz -1 -x --uncorrp -n 5000
  		
	done

done