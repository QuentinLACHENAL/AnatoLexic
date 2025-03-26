import io
import requests
from PIL import Image, ImageTk
import tkinter as tk


def fetch_wikipedia_image(search_term):
    """
    Récupère une image depuis Wikipédia pour le terme de recherche donné.
    Retourne un tuple (img_data, img_url) ou (None, None) si aucune image n'est trouvée.
    """
    print(f"Recherche d'image pour: {search_term}")

    # Essayons d'abord avec un terme anatomique spécifique
    anatomical_term = f"{search_term} anatomie"
    img_data, img_url = try_wikipedia_search(anatomical_term)

    # Si ça ne fonctionne pas, essayons le terme original
    if not img_data:
        img_data, img_url = try_wikipedia_search(search_term)

    # Si ça ne fonctionne toujours pas, essayons la méthode alternative
    if not img_data:
        img_data, img_url = try_alternative_api(search_term)

    return img_data, img_url


def try_wikipedia_search(term):
    """Fonction auxiliaire pour tenter une recherche Wikipedia"""

    # En-têtes pour éviter d'être bloqué par Wikipedia
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    search_term = term.replace(" ", "_")
    api_url = "https://fr.wikipedia.org/w/api.php"

    # Paramètres de l'API
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": search_term,
        "pithumbsize": 500  # Taille de la miniature
    }

    try:
        print(f"Envoi de la requête API Wikipedia pour '{term}'...")
        r = requests.get(api_url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Débogage: afficher la structure complète de la réponse
        print(f"Structure de la réponse: {data.keys()}")

        # Vérifiez si la requête a bien retourné des pages
        if 'query' not in data or 'pages' not in data['query']:
            print("Aucune page trouvée dans la réponse")
            return None, None

        pages = data['query']['pages']
        print(f"Pages trouvées: {len(pages)}")

        for page_id, page_info in pages.items():
            print(f"Page ID: {page_id}, Titre: {page_info.get('title', 'Sans titre')}")

            # Vérifiez d'abord le thumbnail qui est souvent plus fiable
            if "thumbnail" in page_info:
                img_url = page_info["thumbnail"]["source"]
                print(f"Miniature trouvée: {img_url}")

                try:
                    img_response = requests.get(img_url, headers=headers, timeout=15)
                    img_response.raise_for_status()

                    content_type = img_response.headers.get('content-type', '')
                    print(f"Type de contenu: {content_type}")

                    if content_type.startswith('image'):
                        img_data = io.BytesIO(img_response.content)
                        img_data.seek(0)
                        print("Image miniature téléchargée avec succès")
                        return img_data, img_url
                except Exception as e:
                    print(f"Erreur lors du téléchargement de la miniature: {e}")

            # Ensuite, essayez l'image originale si disponible
            if "original" in page_info:
                img_url = page_info["original"]["source"]
                print(f"Image originale trouvée: {img_url}")

                try:
                    img_response = requests.get(img_url, headers=headers, timeout=15)
                    img_response.raise_for_status()

                    content_type = img_response.headers.get('content-type', '')
                    print(f"Type de contenu: {content_type}")

                    if content_type.startswith('image'):
                        img_data = io.BytesIO(img_response.content)
                        img_data.seek(0)
                        print("Image originale téléchargée avec succès")
                        return img_data, img_url
                except Exception as e:
                    print(f"Erreur lors du téléchargement de l'image originale: {e}")

            print(f"Aucune image ou miniature trouvée pour cette page")

        print("Aucune image n'a pu être récupérée")
        return None, None

    except Exception as e:
        print(f"Erreur dans la recherche Wikipedia: {e}")
        return None, None


def try_alternative_api(search_term):
    """Méthode alternative pour récupérer une image si l'API principale échoue."""
    try:
        print(f"Tentative avec méthode anatomique pour '{search_term}'...")

        # En-têtes pour éviter d'être bloqué
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        # Essayons avec une recherche plus spécifique pour l'anatomie
        commons_api_url = f"https://commons.wikimedia.org/w/api.php"

        # Ajouter des termes anatomiques pour filtrer les résultats
        anatomical_search = f"{search_term} anatomie OR anatomy OR os OR squelette OR muscle OR organe"

        commons_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": anatomical_search,
            "srnamespace": "6",  # Namespace 6 pour les fichiers
            "srlimit": "5"  # Augmenter pour avoir plus de chances de trouver une bonne image
        }

        r = requests.get(commons_api_url, params=commons_params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Vérifier chaque résultat jusqu'à trouver une bonne image
        if 'query' in data and 'search' in data['query']:
            for result in data['query']['search']:
                file_title = result['title']

                # Filtrer les images religieuses et autres non pertinentes
                if any(term in file_title.lower() for term in
                       ['sacre', 'jesus', 'religion', 'church', 'icon', 'bible', 'croix']):
                    print(f"Ignoré (religieux): {file_title}")
                    continue

                print(f"Essai avec le fichier: {file_title}")

                # Récupérer l'URL de l'image
                file_api_url = commons_api_url
                file_params = {
                    "action": "query",
                    "format": "json",
                    "titles": file_title,
                    "prop": "imageinfo",
                    "iiprop": "url"
                }

                r = requests.get(file_api_url, params=file_params, headers=headers, timeout=15)
                r.raise_for_status()
                file_data = r.json()

                pages = file_data.get('query', {}).get('pages', {})
                for _, page_info in pages.items():
                    if 'imageinfo' in page_info and len(page_info['imageinfo']) > 0:
                        img_url = page_info['imageinfo'][0]['url']
                        print(f"URL d'image trouvée: {img_url}")

                        img_response = requests.get(img_url, headers=headers, timeout=15)
                        img_response.raise_for_status()

                        img_data = io.BytesIO(img_response.content)
                        img_data.seek(0)
                        print("Image alternative téléchargée avec succès")
                        return img_data, img_url

        print("Aucune image alternative trouvée")
        return None, None

    except Exception as e:
        print(f"Erreur dans la méthode alternative: {e}")
        return None, None


def load_gif_animation(source, label, after_func):
    """
    Charge et affiche une animation GIF dans un label tkinter.
    source: peut être un chemin de fichier (str) ou un objet BytesIO
    label: Label tkinter où afficher l'animation
    after_func: méthode after de tkinter pour planifier l'animation

    Retourne True en cas de succès, False sinon.
    """
    print(f"Début du chargement de l'animation GIF")

    try:
        # Ouvrir le GIF
        if isinstance(source, str):
            print(f"Ouverture du GIF depuis fichier: {source}")
            gif = Image.open(source)
        else:
            print("Ouverture du GIF depuis BytesIO")
            if hasattr(source, 'seek'):
                source.seek(0)  # Assurez-vous de revenir au début
            gif = Image.open(source)

        # Vérifier si c'est bien un GIF
        if gif.format != "GIF":
            print(f"Format non supporté: {gif.format} (seul GIF est supporté pour l'animation)")
            return False

        # Vérifier si c'est un GIF animé
        try:
            n_frames = gif.n_frames
            print(f"Nombre de frames détecté: {n_frames}")
            if n_frames <= 1:
                print("Ce GIF n'est pas animé (une seule frame)")
                # Traiter comme une image statique
                photo = ImageTk.PhotoImage(gif)
                label.config(image=photo)
                label.image = photo
                return True
        except AttributeError:
            print("Impossible de déterminer le nombre de frames")
            return False

        # Extraire toutes les frames
        frames = []
        durations = []

        try:
            for i in range(n_frames):
                gif.seek(i)
                frame = ImageTk.PhotoImage(gif.copy())
                frames.append(frame)

                # Récupérer la durée de cette frame
                duration = gif.info.get('duration', 100)
                if duration == 0:
                    duration = 100  # Valeur par défaut si 0
                durations.append(duration)

                print(f"Frame {i + 1}/{n_frames} chargée (durée: {duration}ms)")
        except Exception as e:
            print(f"Erreur lors du chargement des frames: {e}")
            if len(frames) == 0:
                return False

        print(f"Toutes les frames chargées: {len(frames)}")

        # Définir la fonction d'animation
        def animate(index=0):
            if not frames:
                print("Aucune frame disponible pour l'animation")
                return False

            try:
                # Afficher la frame actuelle
                label.config(image=frames[index])
                label.image = frames[index]  # Garder une référence

                # Préparer la prochaine frame
                next_index = (index + 1) % len(frames)

                # S'assurer que la durée est raisonnable
                delay = max(durations[index], 40)  # Au moins 40ms

                # Planifier l'affichage de la prochaine frame
                after_func(delay, animate, next_index)
            except Exception as e:
                print(f"Erreur pendant l'animation: {e}")
                return False

            return True

        # Démarrer l'animation
        print("Démarrage de l'animation")
        result = animate(0)

        return result

    except Exception as e:
        print(f"Erreur globale dans load_gif_animation: {str(e)}")
        label.config(text=f"Erreur: {str(e)}")
        return False