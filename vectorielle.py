from index import dictionnaire
import cv2 as cv
import math


def show_image(image):
    cv.imshow('Image', image)
    cv.waitKey(0)
    cv.destroyAllWindows()


def evaluate_query(query):
    query = query.lower().strip()
    mots = [mot for mot in query.split() if mot != '+']

    evaluation = {}
    facteur = 0.7

    for i, mot in enumerate(mots):
        evaluation[mot] = round(1.0 * (facteur ** i), 2)

    print("\n" + "_" * 60)
    print("EVALUATION")
    print("_" * 60)
    print(f"Requête: '{query}'")
    print(f"Méthode: Exp | Facteur: {facteur}")
    print("_" * 60)
    for mot, poids in evaluation.items():
        barre = "█" * int(poids * 20)
        print(f"  {mot:20s} → {poids:.2f}  {barre}")
    print("_" * 60 + "\n")

    return evaluation


def crop_features_by_query_length(result_images, query, dictionnaire):
    mots = [mot.lower() for mot in query.split() if mot != '+']
    n = len(mots)

    print("\n" + "_" * 60)
    print(f"Cropping | Nbr mots: {n}")
    print("_" * 60)

    cropped_data = {}

    for image in result_images:
        if image in dictionnaire:
            sorted_features = sorted(dictionnaire[image].items(), key=lambda x: x[1], reverse=True)
            cropped_features = dict(sorted_features[:n])

            adjusted_features = {mot: (poids if mot.lower() in mots else 0.0)
                                 for mot, poids in cropped_features.items()}

            cropped_data[image] = adjusted_features

            print(f"\n {image}:")
            for mot, poids in adjusted_features.items():
                barre = "" * int(poids * 20) if poids > 0 else ""
                print(f"   {mot:15s} → {poids:.2f}  {barre}")

    print("_" * 60 + "\n")
    return cropped_data


def cosine_similarity(query, image_features):
    query_vector = [query[mot] for mot in query]
    image_vector = [image_features.get(mot, 0.0) for mot in query]

    dot_product = sum(q * i for q, i in zip(query_vector, image_vector))
    norm_query = math.sqrt(sum(q ** 2 for q in query_vector))
    norm_image = math.sqrt(sum(i ** 2 for i in image_vector))

    if norm_query == 0 or norm_image == 0:
        return 0.0

    return round(dot_product / (norm_query * norm_image), 4)


def search_images(recherche):
    result_images = []
    mot_cle = recherche.split(" ")
    ou = "+" in mot_cle
    mot_cle_set = set(mot for mot in mot_cle if mot != "+")

    evaluation = evaluate_query(recherche)

    for elem in dictionnaire:
        features_set = set(dictionnaire[elem].keys())
        if (ou and mot_cle_set.intersection(features_set)) or (not ou and mot_cle_set.issubset(features_set)):
            result_images.append(elem)

    cropped_data = crop_features_by_query_length(result_images, recherche, dictionnaire)

    cosine_scores = {}
    for image, features in cropped_data.items():
        score = cosine_similarity(evaluation, features)
        if score > 0:
            cosine_scores[image] = score

    sorted_images = [img for img, _ in sorted(cosine_scores.items(), key=lambda x: x[1], reverse=True)]

    print("\n" + "_" * 60)
    print("SIMILARITÉ COSINUS | Classement des images")
    print("_" * 60)
    for image, score in sorted(cosine_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {image:40s} → {score:.4f}")
    print("_" * 60 + "\n")

    return sorted_images, cosine_scores