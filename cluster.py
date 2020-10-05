# from transformers import BertTokenizer, TFBertForPreTrainingModel

# tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
# model = TFBertForPreTrainingOutput.from_pretrained('bert-base-cased')


from sentence_transformers import SentenceTransformer, util
import torch

embedder = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
corpus = ["The initial project idea at the start of the course was to build a VR campus for OMSCS students to socialise in. While the objective for this research is to motivate the implementation of a OMSCS VR campus, the scope of this project has since been reduced to from actually implementing it to establishing a decentralised, student led social network for the course.",
          "The second part of my project relates to the research based on social learning in VR. I propose a second mode of giving peer feedback - through a MUVE called Hubs \citep{hubs} (which is VR ready but only requires a the use of a web browser and can even run on mobile). Peer reviews groups would be formed from the working groups, with a small number of random links outside the clusters as well. The emergent network will be evaluated based on 2 groups - those who take part in the new mode of peer review and those who do not. We should be able to model the networks from interactions on the Piazza working groups and deduce whether VR peer review sessions have any effect on emergent leadership, network centrality and strength of network links (trust) to name a few. Quantitative analysis will also be undertaken on pre \& post surveys given to students about their perception of the value of peer feedback, again split by whether or not they participated in the VR sessions.",
          "This framework allows you to fine-tune your own sentence embedding methods, so that you get task-specific sentence embeddings. You have various options to choose from in order to get perfect sentence embeddings for your specific task.",
          "This framework provides an easy method to compute dense vector representations for sentences and paragraphs (also known as sentence embeddings). The models are based on transformer networks like BERT / RoBERTa / XLM-RoBERTa etc. and are tuned specificially meaningul sentence embeddings such that sentences with similar meanings are close in vector space.",
          "Notwithstanding the order provided by the CoI Framework, perhaps the main reason that the framework was widely adopted is the methodological guidelines for measuring each of the presences that constituted a community of inquiry. The first of these presences that required rigorous definition and operational rigor was social presence. Extending the original socio-emotional perspective, social presence is most recently defined as the ability of participants to identify with the community (e.g., course of study), communicate purposefully in a trusting environment, and develop inter-personal relationships by way of projecting their individual personalities",
          "Another scenario needs to be considered when scrutinizing the Teaching Presence construct. Much as the more general construct of Presence in an online learning environment can be explained more in depth by separating out Teaching, Social, and Cognitive subfactors, it may be that the Teaching Presence construct's potential bifurcation reflects a strength, and not necessarily a weakness in the subscale's construction. That is, since this factor represents a greater chunk of the total variance, results may simply be pointing to the Teaching Presence subscale itself having two or more subscales. At this early stage of development of measures to operationalize the CoI framework it is important not to assume that a subscale's multidimensionality is necessarily a weakness. Further studies conducted with larger samples and within other contexts will help clarify this issue."]

corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

# Query sentences:
queries = ['The second part of my project relates to the research based on social learning in VR. I propose a second mode of giving peer feedback - through a MUVE called Hubs \citep{hubs} (which is VR ready but only requires a the use of a web browser and can even run on mobile). Peer reviews groups would be formed from the working groups, with a small number of random links outside the clusters as well. The emergent network will be evaluated based on 2 groups - those who take part in the new mode of peer review and those who do not. We should be able to model the networks from interactions on the Piazza working groups and deduce whether VR peer review sessions have any effect on emergent leadership, network centrality and strength of network links (trust) to name a few. Quantitative analysis will also be undertaken on pre \& post surveys given to students about their perception of the value of peer feedback, again split by whether or not they participated in the VR sessions.',
           'If all goes well, at the end of the research project we should have ample motivation to continue to build a full scale social VR campus. For CS6460 the motivation for students to use it would be the peer feedback focus groups, but for other courses a similar peer feedback system might need to be implemented or another student motivation found to encourage the use of the platform. In any case, as leaders emerge and the VR campus network grows, I would expect moderators to appear who will be enthusiastic in mediating focus groups for their respective courses. Luckily in Hubs, moderator super privileges are easily controlled a linked through discord server, and the server side of the campus is hosted on AWS, so the capabilities of scaling the VR campus up significantly are already in place.', 'In order to seed the network, I would like to learn a set of embeddings that represent each students research interests from their research logs. Clustering based on the cosine similarity of these embeddings will create a semantic social network of topics being investigated in the class and within each cluster will be students with a high degree of homophily. I would encourage these clusters to form working groups where they can easily share their research and project updates on Piazza.']


# Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
top_k = 3
for query in queries:
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    cos_scores = cos_scores.cpu()

    # We use torch.topk to find the highest 5 scores
    top_results = torch.topk(cos_scores, k=top_k)

    print("\n\n======================\n\n")
    print("Query:", query)
    print("\nTop 5 most similar sentences in corpus:")

    for score, idx in zip(top_results[0], top_results[1]):
        print(corpus[idx], "(Score: %.4f)" % (score))
