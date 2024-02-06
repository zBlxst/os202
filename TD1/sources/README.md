
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`





## lscpu

```
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         48 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  16
  On-line CPU(s) list:   0-15
Vendor ID:               AuthenticAMD
  Model name:            AMD Ryzen 7 5800H with Radeon Graphics
    CPU family:          25
    Model:               80
    Thread(s) per core:  2
    Core(s) per socket:  8
    Socket(s):           1
    Stepping:            0
    Frequency boost:     enabled
    CPU max MHz:         3200,0000
    CPU min MHz:         1200,0000
    BogoMIPS:            6387.64
    Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl nonstop_tsc cpuid extd_apicid aperfmperf
                          rapl pni pclmulqdq monitor ssse3 fma cx16 sse4_1 sse4_2 movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw ibs skinit wdt tce topoext perfctr
                         _core perfctr_nb bpext perfctr_llc mwaitx cpb cat_l3 cdp_l3 hw_pstate ssbd mba ibrs ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 erms invpcid cqm rdt_a rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xge
                         tbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local clzero irperf xsaveerptr rdpru wbnoinvd cppc arat npt lbrv svm_lock nrip_save tsc_scale vmcb_clean flushbyasid decodeassists pausefilter pfthreshold av
                         ic v_vmsave_vmload vgif v_spec_ctrl umip pku ospke vaes vpclmulqdq rdpid overflow_recov succor smca fsrm
Virtualization features: 
  Virtualization:        AMD-V
Caches (sum of all):     
  L1d:                   256 KiB (8 instances)
  L1i:                   256 KiB (8 instances)
  L2:                    4 MiB (8 instances)
  L3:                    16 MiB (1 instance)
NUMA:                    
  NUMA node(s):          1
  NUMA node0 CPU(s):     0-15
Vulnerabilities:         
  Gather data sampling:  Not affected
  Itlb multihit:         Not affected
  L1tf:                  Not affected
  Mds:                   Not affected
  Meltdown:              Not affected
  Mmio stale data:       Not affected
  Retbleed:              Not affected
  Spec rstack overflow:  Mitigation; safe RET, no microcode
  Spec store bypass:     Mitigation; Speculative Store Bypass disabled via prctl and seccomp
  Spectre v1:            Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:            Mitigation; Retpolines, IBPB conditional, IBRS_FW, STIBP always-on, RSB filling, PBRSB-eIBRS Not affected
  Srbds:                 Not affected
  Tsx async abort:       Not affected
```

*Des infos utiles s'y trouvent : nb core, taille de cache*



## Produit matrice-matrice



### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048) 
------------------|---------|---------|----------------
i,j,k (origine)   | 4.75482 | 451.644 |                
j,i,k             | 4.57382 | 469.516 |    
i,k,j             | 11.2028 | 191.691 |    
k,i,j             | 11.0121 | 195.012 |    
j,k,i             | 0.39222 | 5475.13 |    
k,j,i             | 0.41904 | 5124.85 |    


Avec la représentation des données en mémoire, il est plus intéressant de mettre i en dernier. En effet le cache peut stocker les lignes, ce qu'il peut faire sur deux matrices avec i (lorsqu'il rentre dans la dernière boucle), sur une matrice lorsque k est en dernier, et aucune lorsque j est en dernier.



### OMP sur la meilleure boucle 

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1                 | 4991.08 | 2448.19        | 4965.12
2                 | 9263.41 | 2601.13        | 7214.48
3                 | 12522.2 | 2214.67        | 10932.5
4                 | 14973.6 | 2129.04        | 13227.1
5                 | 17128.4 | 2147.46        | 15588.2
6                 | 19030.5 | 2166.58        | 18172.4
7                 | 20627.6 | 2101.56        | 19036.1
8                 | 22021.1 | 2155.60        | 13076.9




### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    |  |
32                | 21080.1 | 2026.59        | 12664.4
64                | 20639   | 1870.37        | 12850.3
128               | 19767.7 | 2002.37        | 19181.8
256               | 20294.1 | 1932.89        | 19831.7
512               | 20924.4 | 2238.11        | 21531
1024              | 20432   | 2026.86        | 14296.8




### Bloc + OMP



  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|-------------------------------------------------|
A.nbCols       |  1      |         |                |                |               |
512            |  8      |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|
Speed-up       |         |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|



### Comparaison with BLAS

  OMP_NUM  | Blas      | Classic  |
-----------|-----------|----------|
1          | 0.0435733 | 0.422745 |
2          | 0.0328508 | 0.225873 |
3          | 0.0215781 | 0.171921 |
4          | 0.0186065 | 0.142054 |
5          | 0.0174829 | 0.125711 |
6          | 0.0160649 | 0.111675 |
7          | 0.0147406 | 0.101303 |
8          | 0.0144707 | 0.097057 |

Globalement, Blas semble plus rapide d'un facteur 10

## 

Le programme est : parallel_token.py (à noter que token.py ne fonctionne pas à cause des librairies)


## Calcul très approché de pi

Le programme est : mpi_compute_pi.py

Au vu de l'implémentation, et pour une raison qui m'échappe, le speedup vaut 1. 

# Tips 

```
	env 
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
