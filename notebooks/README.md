# Motor Imagery Analysis

Use neural data from the motor imagery experimental task to train a [common spatial pattern](https://sccn.ucsd.edu/download/yijun/pdfs/EMBC05.pdf) (CSP) and [linear discriminant analysis](https://scikit-learn.org/stable/modules/lda_qda.html#lda-qda) (LDA) pipeline for motor imagery classification from neural data. 

Eight CSP components are generated from neural data and they form a spatial filter for neural data to be projected onto. The projected neural data is used as features to train a LDA model to predict motor imagery via supervised learning. The CSP spatial filters and trained motor imagery classifier are saved and can be used for BCI tasks for realtime neural decoding (for example, the Pong video game).