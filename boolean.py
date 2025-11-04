from index import dictionnaire
import cv2 as cv
import os

def search_images(recherche):
    result_images = []
    ou = False
    mot_cle = recherche.lower().split(" ")

    if "+" in mot_cle:
        ou = True
        mot_cle.remove("+")

    mot_cle = set(mot_cle)

    for elem in dictionnaire:
        features = dictionnaire[elem]
        print(features)
        features = set(features)
        print(features)
        if ou:
            common_features = mot_cle.intersection(features)
            if common_features:
                result_images.append(elem)
        else:
            if mot_cle.issubset(features):
                result_images.append(elem)

    return result_images


def show_image(image, max_width=800, max_height=600):
    h, w = image.shape[:2]

    # (keep aspect ratio)
    scale = min(max_width / w, max_height / h, 2.0)  # don't enlarge small images

    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv.resize(image, (new_w, new_h), interpolation=cv.INTER_AREA)
    cv.imshow("Image", resized)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    recherche = input("Entrer un mot pour rechercher: ")
    result_images = search_images(recherche)

    bas_path = "images/"

    if not result_images:
        print("0 Images trouvées")
    else:
        print(f"{len(result_images)} Images Trouvées")
        for image in result_images:
            full_path = os.path.join(bas_path, image)
            print(full_path)
            image = cv.imread(full_path)
            show_image(image)
