from index import dictionnaire
import cv2 as cv

def show_image(image):
    cv.imshow('Image', image)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == '__main__':
    print("Entrer un mot pour rechercher: ")
    recherche = input()
    result_images = []

    path = 'images/'
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
            path += image
            print(path)
            image = cv.imread(path)
            show_image(image)