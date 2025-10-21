from index import dictionnaire
import cv2 as cv
import os 

def show_image(image, max_width=800, max_height=600):
    h, w = image.shape[:2]

    #(keep aspect ratio)
    scale = min(max_width / w, max_height / h, 2.0)  # don't enlarge small images

    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv.resize(image, (new_w, new_h), interpolation=cv.INTER_AREA)
    cv.imshow('Image', resized)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == '__main__':
    recherche = input("Entrer un mot pour rechercher: ").lower()
    result_images = []

    bas_path = 'images/'
    ou = False
    mot_cle = recherche.split(' ')
    
    if '+' in mot_cle:
        ou = True

    mot_cle = set(mot_cle)

    for elem in dictionnaire:
        features = dictionnaire[elem]
        features = set(features)
        if ou:
            common_features = mot_cle.intersection(features)
            if common_features:
                result_images.append(elem)

        else:
            if mot_cle.issubset(features):
                result_images.append(elem)

    if not result_images:
        print("0 Images trouvées")
    else: 
        print(f'{len(result_images)} Images Trouvées')
        for image in result_images:
            full_path = os.path.join(bas_path, image)
            print(full_path)
            image = cv.imread(full_path)
            show_image(image)