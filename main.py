import struct
import pandas as pd


def float_to_binary64(value):
    getBin = lambda x: x > 0 and str(bin(x))[2:] or "-" + str(bin(x))[3:]

    val = struct.unpack('Q', struct.pack('d', value))[0]
    return getBin(val)


def binary_to_float(value):
    hx = hex(int(value, 2))
    return struct.unpack("d", struct.pack("q", int(hx, 16)))[0]


class CodageDecodageArithmetique:
    """Une classe pour le codage et le décodage des caractères en utilisant le codage arithmétique"""

    def __init__(self) -> None:
        self.sequence = ''
        self.code = 0
        self.intervalle_frequence: dict[str, tuple[float, float]] = {}
        self.dictionnaire_frequence: dict[str, float] = {}
        self.intervalle_sequence_compresse: tuple[float, float] = (0, 1)

    def coder(self, sequence: str) -> float:
        self.sequence = sequence
        print(f"Codage arithmétique de la séquence '{sequence}'\n\n")

        self.crer_intervalle_frequence()
        # Si Séquence précédente [a, b[ et Caractère courant [c, d[
        # alors Sequence courante [a + c * (b - a), a + d * (b - a)[
        # print(self.intervalle_fréquence)

        self.intervalle_sequence_compresse = (0, 1)
        print(f"  : [0, 1[")
        # Calculer le nouvel intervalle compresse pour chaque caractère de la sequence a compresser
        for caractere in self.sequence:
            a, b = self.intervalle_sequence_compresse
            c, d = self.intervalle_frequence[caractere]

            self.intervalle_sequence_compresse = (a + c * (b - a), a + d * (b - a))
            print(f"{caractere} : [{self.intervalle_sequence_compresse[0]},"
                  f"{self.intervalle_sequence_compresse[1]}[")

        print("\nL'intervalle final est le suivant")
        print(f"{self.sequence} : [{self.intervalle_sequence_compresse[0]},"
              f"{self.intervalle_sequence_compresse[1]}[")
        print("\n")

        # Determiner un code
        a, b = self.intervalle_sequence_compresse
        largeur = str(b - a).split('.')[1]
        nombre_zero_avant_premier_chiffre = 0
        for byte in largeur:
            if byte == '0':
                nombre_zero_avant_premier_chiffre += 1
            else:
                break

        # La longueur minimale comprend le 0 avant la virgule, le point,
        # les zéros après et deux chiffres après pour être ok
        longueur_minimale_code = 2 + nombre_zero_avant_premier_chiffre + 2
        # on tranche à la moitié de l'intervalle pour réduire les erreurs
        self.code = str((a + b) / 2)[:longueur_minimale_code]
        self.code = float(self.code)

        print("Nous prenons la moyenne de l'intervalle")
        print(f"On obtient alors le code : {self.code}")
        print("\n")

        return self.code

    def coder_en_ieee754(self, sequence: str):
        code = float_to_binary64(self.coder(sequence))
        # code = '0' + code
        print(f"Avec le format IEEE 754, voici le code . {code}")
        # code = code[:64]
        print("\n")
        return code

    def decoder(self, code: float, dictionnaire_frequence: dict[str, float],
                intervalle_frequence: dict[str, tuple[float, float]], nombre_caractere=15):
        self.code = code
        self.intervalle_frequence = intervalle_frequence
        self.dictionnaire_frequence = dictionnaire_frequence

        sequence = ''
        nombre_recu = self.code
        for i in range(nombre_caractere):
            caractere = self.obtenir_caractere_apartir_code(nombre_recu)

            # Arrêt si caractère introuvable
            if not caractere:
                print(f"Erreur: Le nombre '{nombre_recu}' n'a pas de correspondance")
                return

            print(f"| {nombre_recu} => {caractere} |")
            sequence += caractere
            a, b = self.intervalle_frequence[caractere]
            nombre_recu = (nombre_recu - a) / self.dictionnaire_frequence[caractere]

        self.sequence = sequence
        print(f"Le décodage du code {self.code} donne")
        print(self.sequence)

    def obtenir_caractere_apartir_code(self, code: float) -> str | None:
        for caractere in self.intervalle_frequence:
            a, b = self.intervalle_frequence[caractere]
            if a <= code < b:
                return caractere

    def crer_intervalle_frequence(self):
        # Il faut au moins 1 caractère et au plus 15 caractères
        longueur_sequence = len(self.sequence)
        if longueur_sequence <= 0 or longueur_sequence > 15:
            print("Veuillez recommencer le codage")
            print("Il faut au moins 1 caractère et au plus 15 caractères")
            return

        # Compter les occurrences
        dictionnaire_occurrence: dict[str, int] = {}
        for caractere in self.sequence:
            if caractere in dictionnaire_occurrence:
                dictionnaire_occurrence[caractere] += 1
            else:
                dictionnaire_occurrence[caractere] = 1
        print("Le nombre d'occurrence de chaque caractère")
        print(pd.Series(dictionnaire_occurrence))
        print("\n")

        # Calculer les fréquences
        dictionnaire_frequence: dict[str, float] = {}
        for caractere in dictionnaire_occurrence:
            dictionnaire_frequence[caractere] = dictionnaire_occurrence[caractere] / longueur_sequence

        self.dictionnaire_frequence = dictionnaire_frequence
        print("Les fréquences associées sont les suivantes")
        print(pd.Series(dictionnaire_frequence))
        print("\n")

        # Calculer les intervalles de fréquence
        caracteres = list(self.dictionnaire_frequence)
        for i in range(len(caracteres)):
            caractere_courant = caracteres[i]
            if i == 0:
                frequence_courante = self.dictionnaire_frequence[caractere_courant]
                self.intervalle_frequence[caractere_courant] = (0, frequence_courante)
            else:
                caractere_precedent = caracteres[i - 1]
                borne_superieure_precedente = self.intervalle_frequence[caractere_precedent][1]
                frequence_courante = self.dictionnaire_frequence[caractere_courant]
                self.intervalle_frequence[caractere_courant] = (borne_superieure_precedente,
                                                                borne_superieure_precedente + frequence_courante)
        # La derniere borne a 1
        self.intervalle_frequence[caracteres[-1]] = (self.intervalle_frequence[caracteres[-1]][0], 1)

        print("Les calculs aboutissent aux différents intervalles de fréquence suivants")
        print(pd.Series(self.intervalle_frequence))
        print("\n")

        return self.intervalle_frequence

    def obtenir_dictionnaire_frequence(self):
        return self.dictionnaire_frequence

    def obtenir_intervalle_frequence(self):
        return self.intervalle_frequence


if __name__ == '__main__':
    # Codage
    sequence_a_coder = input("Entrez le texte à coder \n")
    codeur = CodageDecodageArithmetique()
    code = codeur.coder(sequence_a_coder)
    dictionnaire_frequence = codeur.obtenir_dictionnaire_frequence()
    intervalle_frequence = codeur.obtenir_intervalle_frequence()

    # Décodage
    decodeur = CodageDecodageArithmetique()
    decodeur.decoder(code, dictionnaire_frequence, intervalle_frequence, nombre_caractere=len(sequence_a_coder))
