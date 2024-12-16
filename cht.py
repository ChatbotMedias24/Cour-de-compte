import streamlit as st
import openai
import streamlit as st
from dotenv import load_dotenv
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from streamlit_chat import message  # Importez la fonction message
import toml
import docx2txt
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import docx2txt
from dotenv import load_dotenv
if 'previous_question' not in st.session_state:
    st.session_state.previous_question = []

# Chargement de l'API Key depuis les variables d'environnement
load_dotenv(st.secrets["OPENAI_API_KEY"])

# Configuration de l'historique de la conversation
if 'previous_questions' not in st.session_state:
    st.session_state.previous_questions = []

st.markdown(
    """
    <style>

        .user-message {
            text-align: left;
            background-color: #E8F0FF;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: 10px;
            margin-right: -40px;
            color:black;
        }

        .assistant-message {
            text-align: left;
            background-color: #F0F0F0;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: -10px;
            margin-right: 10px;
            color:black;
        }

        .message-container {
            display: flex;
            align-items: center;
        }

        .message-avatar {
            font-size: 25px;
            margin-right: 20px;
            flex-shrink: 0; /* Empêcher l'avatar de rétrécir */
            display: inline-block;
            vertical-align: middle;
        }

        .message-content {
            flex-grow: 1; /* Permettre au message de prendre tout l'espace disponible */
            display: inline-block; /* Ajout de cette propriété */
}
        .message-container.user {
            justify-content: flex-end; /* Aligner à gauche pour l'utilisateur */
        }

        .message-container.assistant {
            justify-content: flex-start; /* Aligner à droite pour l'assistant */
        }
        input[type="text"] {
            background-color: #E0E0E0;
        }

        /* Style for placeholder text with bold font */
        input::placeholder {
            color: #555555; /* Gris foncé */
            font-weight: bold; /* Mettre en gras */
        }

        /* Ajouter de l'espace en blanc sous le champ de saisie */
        .input-space {
            height: 20px;
            background-color: white;
        }
        .input-space {
        margin-top: 1px;
        margin-bottom: 1px;
    }
        @keyframes dot-blink {
            0% { content: ""; }
            33% { content: "."; }
            66% { content: ".."; }
            100% { content: "..."; }
        }
        .loading-message {
        margin-top: 1;
        padding-top: 1px;
        font-size: 20px;
        font-weight: bold;
        white-space: nowrap;
        animation: dot-blink 1.5s infinite step-start;
        
        }
    
    </style>
    """,
    unsafe_allow_html=True
)
# Sidebar contents
textcontainer = st.container()
with textcontainer:
    logo_path = "medi.png"
    logoo_path = "NOTEPRESENTATION.png"
    st.sidebar.image(logo_path,width=150)
   
    
st.sidebar.subheader("Suggestions:")
questions = [
    "Donnez-moi un résumé du rapport ",
    "Quels sont les principaux facteurs ayant contribué à l'amélioration de la croissance économique en 2023 ?",
    "Quelles stratégies sont proposées pour répondre au stress hydrique au Maroc ?",      
    "Comment la Cour recommande-t-elle de surmonter les retards liés à la digitalisation de l'administration publique ?",
    """Quel est l'impact des recommandations de la Cour sur la gestion des finances publiques à moyen et long terme ?"""
]
# Initialisation de l'historique de la conversation dans `st.session_state`
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = StreamlitChatMessageHistory()

if 'previous_questions' not in st.session_state:
    st.session_state.previous_questions = []

# Ajouter une nouvelle question au début de la liste
def add_question(question):
    st.session_state.previous_questions.insert(0, question)
def main():
    text=r"""
    
Majesté,
La publication du rapport annuel de la Cour des comptes pour l’exercice
2023-2024 coïncide cette année avec la célébration, par le peuple
marocain, du vingt-cinquième anniversaire de l’accession de Votre
Majesté au Trône de Vos Glorieux Ancêtres.
Notre pays a entrepris, sous le règne de Votre Majesté, de profondes
réformes et a connu un développement significatif dans tous les domaines.
De grands chantiers économiques et sociaux ont été lancés, parallèlement
à la poursuite des réformes politiques et institutionnelles, répondant ainsi
aux aspirations du peuple marocain. Ces chantiers et réformes placent la
dignité et le bien-être du citoyen marocain au centre de leurs priorités.
Sur le plan international, outre l’intensification des conflits géopolitiques,
le monde est aujourd'hui confronté à de nombreux défis, parmi lesquels le
changement climatique, les catastrophes naturelles qui en résultent et la
raréfaction des ressources en eau, ainsi que les risques sanitaires
principalement liés à la prolifération des épidémies. Tous ces défis ont pesé
sur l'économie mondiale, qui traverse une période difficile, marquée par un
ralentissement de la croissance et des niveaux élevés des taux d’inflation.
Ainsi, le taux de croissance a régressé de 3,5% à 3,2% entre 2022 et 2023,
tout en observant des écarts significatifs dans l’évolution de la croissance
entre les différents pays du monde. Par ailleurs, la croissance mondiale
devrait se stabiliser en 2024 et 2025, avec des taux respectifs de 3,2% et
3,3%, selon les prévisions du Fonds monétaire international.
Quant à l'inflation, l'année 2023 a connu une légère baisse à l'échelle
mondiale, s'établissant à 6,7% après avoir atteint un niveau
exceptionnellement élevé de 8,7% en 2022. Cette diminution s'explique
principalement par des politiques monétaires restrictives ainsi que par la
baisse des prix des matières premières. De plus, les pressions
inflationnistes devraient continuer à s'atténuer en 2024 et 2025, pour
atteindre respectivement 5,9% et 4,5%.
Au niveau national, malgré ce contexte international difficile et complexe,
marqué par des transformations rapides et souvent imprévisibles, et en
dépit de plusieurs années consécutives de sécheresse sévère et de stress
hydrique, l'année 2023 a pu enregistrer une amélioration de divers
indicateurs relatifs à l'économie nationale et aux finances publiques.
Ainsi, la croissance a affiché une amélioration, passant de 1,5% en 2022 à
3,4% en 2023. Selon les prévisions de Bank Al-Maghrib, cette croissance
devrait se replier en 2024 pour atteindre 2,8%, avant de remonter à 4,4%
d’ici la fin de l’année 2025.



                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              5
    S’agissant du taux d'inflation, il s'est établi à 6,1% en 2023 contre 6,6% en
    2022. D’après les prévisions de Bank Al-Maghrib, il devrait baisser à 1,3%
    en 2024, puis atteindre 2,5% en 2025.
    Concernant les finances publiques, les recettes ordinaires du budget
    général de l'État ont atteint 324 MMDH, soit une augmentation de 22,2
    MMDH par rapport à 2022 (+7,4%). Cette progression est essentiellement
    due à l'augmentation des recettes fiscales de 13,9 MMDH (+5,6%) et des
    recettes non fiscales de 8,2 MMDH (+16,8%). Cette dynamique positive
    s'est poursuivie en 2024, avec des recettes atteignant, à fin septembre 2024,
    environ 261,9 MMDH, contre 233,5 MMDH sur la même période en 2023
    (+12,2%). L’augmentation des recettes est principalement attribuée à la
    poursuite de la mise en œuvre de la réforme fiscale, ainsi que par l'impact
    de l'inflation élevée, notamment sur les recettes douanières.
    En ce qui concerne les dépenses ordinaires du budget de l'État, elles se sont
    établies à 293 MMDH, marquant, ainsi, une hausse de 5,1 MMDH par
    rapport à 2022 (+1,8%). Les dépenses d'investissement ont, quant à elles,
    augmenté de 18%, passant de 93,8 MMDH à 110,8 MMDH entre 2022 et
    2023. Cette augmentation s’explique essentiellement par l'accélération de
    la réalisation de certains projets structurants dans le cadre du Programme
    National d'Approvisionnement en Eau Potable et d'Irrigation 2020-2027,
    ainsi que par la poursuite du soutien apporté à certains établissements
    publics, dont la situation financière a été négativement impactée par la
    hausse des prix des matières énergétiques en 2022.
    Par ailleurs, à l’instar de l’année 2022, le taux du déficit budgétaire, a
    enregistré une diminution en 2023, s’établissant à 4,4% du PIB contre
    5,4% en 2022. Selon les prévisions de Bank Al-Maghrib, ce taux se
    stabiliserait à 4,4% à fin 2024 avant de poursuive sa tendance baissière en
    2025 pour atteindre 3,9%.
    S’agissant de l’endettement, l’encours de la dette du Trésor a augmenté de
    6,8% par rapport à 2022, atteignant 1.016,6 MMDH en 2023, ce qui
    représente 69,5% du PIB, contre 71,5% en 2022. Ainsi, la dette extérieure
    a connu une hausse de 10,8% par rapport à 2022, s’élevant à
    253,6 MMDH, tandis que la dette intérieure a progressé de 5,6%,
    atteignant 763 MMDH.
    La maîtrise de l'évolution du déficit budgétaire et du niveau d’endettement
    en les réduisant respectivement, selon les objectifs et les résultats
    escomptés, à 3% d'ici fin 2026 et 66,3% au cours de l'année 2027, constitue
    un levier essentiel pour améliorer la performance des finances publiques.
    Toutefois, l'atteinte de ces objectifs reste tributaire, principalement, de la
    performance de l’économie nationale et de son impact sur la pérennité du



       Rapport annuel de la Cour des comptes au titre de 2023-2024
6                    - Principaux axes -
taux de croissance, ainsi que de l'augmentation du PIB, en termes
nominaux, et de son effet sur les recettes de l’État.

Majesté,
Les finances publiques de notre pays ont maintenu leur résilience, malgré
un contexte difficile et instable, affichant une amélioration notable de
plusieurs indicateurs, notamment la hausse des recettes du budget général
de l’État et la réduction du déficit budgétaire. Toutefois, le principal défi
consiste à consolider ces acquis afin de renforcer la solidité des finances
publiques et de garantir leur soutenabilité.
La conjoncture actuelle requiert de dégager des marges financières
nécessaires pour financer les grandes réformes engagées par notre pays.
Au premier rang de celles-ci figure la consolidation de l’État social, ainsi
que la mise en œuvre de programmes et projets visant à atténuer les effets
des changements climatiques et de la raréfaction des précipitations, tout en
répondant aux soucis de préservation du pouvoir d’achat des citoyens.
De plus, les répercussions des catastrophes naturelles survenues au cours
des deux dernières années, ainsi que les préparatifs liés aux engagements
de notre pays pour accueillir des événements sportifs internationaux de
grande envergure, rendent indispensable la mobilisation de ressources
supplémentaires pour couvrir les charges financières associées.
Face à ces enjeux, la mise en œuvre de la réforme fiscale, initiée en 2022,
se poursuit avec comme objectif la mise en place un système fiscal
équitable, efficace, incitatif pour l’investissement et capable de générer des
ressources financières stables et durables. Par ailleurs, l’accélération de la
réforme du secteur des établissements et entreprises publics, ainsi que la
réforme du système d’investissement, notamment le défi lié à
l’augmentation de la part de l’investissement privé, contribueraient
également à améliorer le système d’allocation des ressources, dégager des
marges budgétaires et à alléger la pression sur les finances publiques.
Outre la nécessité d’accroître les recettes de l’État, il est indispensable de
poursuivre la rationalisation et l’optimisation des dépenses en les orientant
vers les domaines prioritaires, d'autant plus que celles-ci ont enregistré une
augmentation significative et continue, dépassant 42% durant la période
2021-2023. À ce niveau, l’amélioration de l’efficacité des dépenses
publiques dans leur ensemble, et en particulier celle des investissements
publics, revêt une importance capitale et constitue une réforme prioritaire
des finances publiques.
En effet, notre pays a mis en place plusieurs stratégies nationales et
sectorielles, ainsi qu'un ensemble de programmes et projets publics, visant



                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              7
    à réhabiliter les infrastructures et à améliorer la qualité des services offerts,
    ce qui devrait stimuler les investissements privés et attirer les capitaux
    étrangers. Malgré les acquis réalisés dans le cadre de ces stratégies,
    programmes et projets, leur impact sur le citoyen et sur l'économie
    nationale doit davantage être amélioré. Cela nécessite, d’après les
    différents diagnostics réalisés sur l'investissement public, de renforcer la
    culture de gestion axée sur les résultats et d'adopter une approche intégrée
    de gestion dans toutes ses dimensions relatives à la programmation, à la
    mise en œuvre, au suivi, à la supervision et à l’évaluation. L'objectif est de
    rendre les investissements publics plus conformes aux critères d'efficacité,
    d'efficience et d'économie, surtout dans un contexte marqué par des
    besoins croissants et une multitude de défis.
    À cet égard, les juridictions financières ont, depuis plusieurs années, œuvré
    à l'évaluation d'un ensemble de stratégies, de programmes et de projets
    publics, couvrant principalement les domaines de l'éducation, de la santé,
    de l’habitat, de l'agriculture, de la pêche, des équipements de base, des
    infrastructures, de l'énergie ainsi que d'autres secteurs importants. Une
    attention particulière a été accordée à leur mise en œuvre au niveau
    territorial, dans le cadre de diverses missions de contrôle, notamment celle
    liée au Programme de Réduction des Disparités Territoriales et Sociales,
    ainsi qu'aux projets publics faisant face à des difficultés d'exécution ou
    d'exploitation et aux programmes et projets de développement territorial
    intégré.
    À travers ces missions d'évaluation, les juridictions financières ont
    enregistré un ensemble de facteurs qui entravent l'atteinte des objectifs
    fixés dans le cadre de ces programmes et projets publics, et par conséquent
    leur impact sur les citoyens et l'économie nationale. Ces facteurs sont liés
    aux différentes étapes d'élaboration et de mise en œuvre de ces
    programmes et projets.
    Ainsi, les juridictions financières ont attiré l’attention, dans plusieurs
    rapports, sur un ensemble d’insuffisances dans la gestion des
    investissements publics. Celles-ci se manifestent principalement par des
    études préalables peu fiables, voire inexistantes, ce qui entraîne une
    imprécision dans la définition des besoins et leur classement sur l’échelle
    des priorités. De plus, les spécificités socioculturelles des territoires ne sont
    souvent pas prises en compte au préalable, tout comme les aspects liés à la
    gestion et l’opérationnalisation des infrastructures réalisées, ce qui soulève
    de nombreuses contraintes quant à leur exploitation et leur durabilité. Par
    ailleurs, la problématique de la mobilisation du foncier est considérée
    comme l'un des principaux obstacles à l'investissement public. En effet, il
    est encore fréquent que des projets publics soient programmés sans



       Rapport annuel de la Cour des comptes au titre de 2023-2024
8                    - Principaux axes -
s’assurer de la disponibilité du foncier et de son adéquation, ce qui conduit
à la non réalisation de ces projets et retarde leur mise en œuvre.
Les autres lacunes sont principalement liées à la gouvernance, en
particulier au niveau du pilotage et de la supervision, ainsi qu'à
l’insuffisance de la coordination entre les parties prenantes impliquées
dans les programmes et projets publics. De plus, les capacités de gestion
des organismes publics chargés de la mise en œuvre de ces programmes et
projets demeurent souvent limitées, notamment au niveau territorial.
A la lumière de ces insuffisances, et pour accroître l'efficacité des dépenses
publiques tout en instaurant véritablement une culture de gestion axée sur
les résultats, et ainsi renforcer l'efficacité des investissements publics et
atteindre les résultats escomptés, il est essentiel d'améliorer les
mécanismes de ciblage, de programmation et de priorisation. L’approche
à mener doit se faire d'études préalables impliquant toutes les parties
concernées et s’appuyant sur des indicateurs objectifs et pertinents et
partagés par l’ensemble des acteurs. Il est également nécessaire de mettre
en place et d'activer des mécanismes garantissant la coordination entre les
différents partenaires, ainsi qu’un suivi et une évaluation réguliers. En
outre, il convient de renforcer les capacités de gestion des organismes en
charge des projets, de sélectionner ceux qui sont les mieux placés pour les
réaliser, ainsi que d'optimiser l'utilisation des expertises et des ressources
humaines disponibles aux niveaux central et territorial, et capitaliser,
surtout sur le retour d’expérience.

Majesté,
Au vu de son statut constitutionnel en tant qu’institution supérieure de
contrôle des finances publiques, et consciente des missions qui lui sont
confiées ainsi que des défis que la conjoncture actuelle impose, la Cour des
comptes, guidée par les principes énoncés dans les différents discours de
Votre Majesté, appelant à garantir les conditions d’une vie décente aux
citoyens et à répondre avec efficacité à leurs besoins, veille à
l’accompagnement des grandes réformes que connaît notre pays et à la
participation de manière efficace et efficiente dans le processus de
développement. L’objectif est que les citoyens puissent constater
concrètement et sur leur vécu l’impact des programmes et projets réalisés
par l’État et par les autres acteurs publics.
C'est dans cet esprit que la Cour des comptes a fait du renforcement de
l'impact de ses travaux un objectif principal de ses orientations stratégiques
pour la période 2022-2026. Elle s’attache ainsi à mettre en évidence les
manifestations concrètes de cet impact et les pistes d'amélioration tout au
long des différentes étapes de l'exécution de ses missions de contrôle.


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              9
     Ainsi, l’impact des travaux de la Cour et des Cours régionales des comptes
     ne se limite pas à la mise en œuvre des recommandations émises, qui, dans
     certains cas, peuvent nécessiter des délais relativement longs. Il se
     manifeste également avant même que les procédures liées aux différentes
     compétences ne soient totalement épuisées. En effet, les travaux des
     juridictions financières produisent souvent des effets immédiats, d’ordre
     financier ou correctif, à travers la correction de pratiques irrégulières, la
     prévention des risques de gestion, et le renforcement des systèmes de
     gouvernance, de contrôle interne, ainsi que l’amélioration des mécanismes
     de planification et de programmation.
     À cet égard, pour la période 2023-2024, les juridictions financières ont
     enregistré que des mesures correctives ont été prises suite aux observations
     faites dans le cadre des missions de contrôle de la gestion, avec un impact
     direct sur les finances des organismes concernés, estimé à environ
     139 MDH. De plus, certains organismes publics ont pu se faire restituer
     un montant total dépassant 28 MDH, et ce, avant même que les jugements
     et arrêts définitifs ne soient rendus par ces juridictions.
     La volonté des juridictions financières de donner un impact concret à leur
     action se reflète aussi à travers une programmation de leurs travaux fondée
     sur une approche intégrée, reposant sur l’analyse des risques, ainsi que les
     critères de l’actualité, de la prise en considération des défis immédiats et
     de la prévision ainsi que de l’anticipation des enjeux futurs.
     Par cette approche, la Cour vise à cibler les sujets prioritaires liés à la
     gestion des finances publiques, tels que la problématique de l'endettement
     et de la soutenabilité des finances publiques, ainsi que ceux qui impactent
     l'environnement des politiques publiques dans un contexte marqué par les
     avancées technologiques, les changements climatiques et les crises
     géopolitiques et économiques. Cette démarche a pour objectif de
     sensibiliser les décideurs et les gestionnaires publics aux risques potentiels,
     tout en mettant en avant les opportunités existantes.
     L’approche de contrôle adoptée par les juridictions financières a évolué
     d’un contrôle axé presque exclusivement sur la régularité des actes de
     gestion vers une évaluation de la performance la gestion publique, en
     s'appuyant sur les critères d’économie, d’efficience, d’efficacité et
     d’impact. La nouvelle démarche s’aligne sur les évolutions ayant marqué
     la gestion de la chose publique en général et celle des finances publiques
     en particulier, visant à renforcer la performance et à promouvoir la culture
     de gestion axée sur les résultats, plutôt que sur les moyens.
     Dans ce contexte, et en application des directives éclairées de Votre
     Majesté, exprimées dans le Discours Royal à l’occasion de l'ouverture
     du Parlement le 13 octobre 2017, qui appelle la Cour des Comptes à exercer


        Rapport annuel de la Cour des comptes au titre de 2023-2024
10                    - Principaux axes -
pleinement ses missions de suivi et d'évaluation des projets publics dans
les différentes régions du Royaume, les juridictions financières ont orienté
davantage leurs activités de contrôle vers l’évaluation des stratégies,
programmes et projets publics. La Cour et les Cours régionales des
comptes continueront à renforcer cette orientation et à accorder une place
plus importante aux évaluations dans leurs futurs travaux, en veillant à ce
qu'elles ne se limitent pas à des évaluations postérieures, mais incluent
également des évaluations concomitantes. Cette approche est essentielle
pour identifier et signaler, à temps, les risques associés à la stratégie, au
programme ou au projet évalué, permettant ainsi de formuler des
recommandations pour surmonter ces risques ou, au moins, en atténuer les
impacts, et partant, atteindre les objectifs fixés tout en concrétisant l’effet
escompté.
Selon cette orientation, les missions de contrôle, dont les principaux
résultats sont insérés dans le rapport annuel 2023-2024, se caractérisent par
leur diversité et abordent des sujets et problématiques d'actualité relatifs
aux secteurs financier, social et environnemental, ainsi qu'aux
infrastructures et à l’habitat. Elles incluent également des thématiques liées
au développement territorial et à la gestion des équipements publics
locaux. En outre, des sujets ont été examinés dans le cadre du suivi, par la
Cour, des grands chantiers de réforme de notre pays, à savoir la
problématique de l'eau, la régionalisation avancée, la protection sociale,
l'investissement, les établissements et entreprises publics, ainsi que la
réforme fiscale.
Ainsi, et dans le cadre de ses travaux de contrôle et de suivi de la mise en
œuvre des grands chantiers de réforme, la Cour a accordé une attention
particulière à deux problématiques d’actualité, en l’occurrence celles de
l'eau et des changements climatiques, qui représentent de réelles
contraintes tant pour l’activité économique que pour les citoyens. En effet,
le stress hydrique constitue l'un des défis majeurs auxquels notre pays est
confronté, en raison de plusieurs facteurs, notamment la succession des
années de sécheresse et l'impact des changements climatiques sur les
ressources hydriques nationales. À cela s'ajoutent la demande croissante et
les conséquences qui en résultent, particulièrement la surexploitation des
ressources hydriques existantes. Cette problématique met également en
évidence des lacunes dans la gouvernance et la mise en œuvre des
stratégies et programmes adoptés dans ce domaine.
Ainsi, la sécurité hydrique et la satisfaction de la demande en ressources
en eau constituent une priorité majeure pour notre pays, bénéficiant d'une
attention particulière de la part de Votre Majesté.




                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              11
     Dès l’aube de l'indépendance, notre pays a pris conscience des défis liés à
     la rareté de l'eau et a agi en adoptant des politiques proactives de gestion
     des ressources hydriques. En plus de la politique de construction de
     barrages, visant à améliorer la durabilité des ressources en eau et à
     renforcer la capacité à faire face aux défis environnementaux et
     économiques, de nombreux projets ont été réalisés pour garantir
     l'approvisionnement en eau potable de la population. Il s’agit, notamment,
     du programme national intégré d'approvisionnement en eau potable en
     milieu rural, de la Stratégie Nationale de l'Eau 2009-2030, ainsi que du
     Programme National d'Approvisionnement en Eau Potable et d’Irrigation
     2020-2027. Ces mesures ont permis de mettre en place des infrastructures
     et équipements hydrauliques importants, ayant contribué à atténuer la
     gravité de la situation actuelle.
     Dans la même sillage, notre pays a œuvré pour adapter le cadre juridique
     relatif à la gestion de l'eau, afin de répondre aux défis associés à cette
     ressource vitale. En outre, il est essentiel que cette approche soit
     accompagnée d'autres mesures et procédures dans le cadre d'une vision
     multidimensionnelle, en vue d'assurer une intégration et une convergence
     entre les secteurs de l'eau, de l'agriculture et de l'énergie, ainsi qu'un
     alignement et une synergie entre leurs stratégies au niveau territorial.
     À cet égard, il devient impératif d’orienter les projets de construction des
     barrages vers les régions bénéficiant de fortes précipitations, afin d'éviter
     toute perte des apports hydriques et d'en maximiser l’exploitation. Par
     ailleurs, il est essentiel d’activer la réalisation des projets d’interconnexion
     des bassins hydrauliques, en tant que solution innovante pour atténuer la
     pénurie d'eau dans les zones souffrant d'une diminution de leurs ressources
     hydriques, et pour réduire les disparités territoriales dans la répartition de
     ces ressources. Enfin, il convient de développer davantage les projets
     visant la mobilisation des ressources non conventionnelles, tels que le
     traitement des eaux usées et le dessalement de l'eau.
     Par ailleurs, il est essentiel d'accélérer la transition vers un système
     d'irrigation localisée, afin d'optimiser l'utilisation de l'eau en agriculture,
     ainsi que de renforcer le recours aux énergies renouvelables pour mobiliser
     les ressources en eau. Il est également important de promouvoir la
     recherche scientifique dans le domaine de l'eau et d'encourager la
     collaboration avec les universités et les laboratoires de recherche, en vue
     de contribuer à l'élaboration de solutions locales aux problématiques
     environnementales, en l’occurrence celles liées à l’eau et au sol. De plus,
     il convient de mobiliser tous les canaux de communication disponibles
     pour sensibiliser les entreprises, les ménages et les citoyens à la nécessité
     d’adopter des comportements responsables en vue de rationaliser la



        Rapport annuel de la Cour des comptes au titre de 2023-2024
12                    - Principaux axes -
consommation d’eau, et d’activer, le cas échéant, les mécanismes
répressifs des comportements irresponsables.
Sur un autre registre, la Cour des comptes a continué le suivi de la mise en
œuvre de la réforme du système de développement, de promotion et
d’attraction de l'investissement, compte tenu de son importance pour
dynamiser l’économie nationale, générer de la richesse, créer des
opportunités d'emploi et réduire les disparités territoriales et sociales.
Malgré les avancées réalisées dans la mise en œuvre de cette réforme,
notamment en ce qui concerne le cadre stratégique relatif au
développement de l'investissement privé, ainsi que l'adoption de la charte
de l’investissement et la feuille de route stratégique pour la période 2023-
2026, visant à améliorer le climat des affaires et à lever les obstacles à son
développement, il demeure essentiel d'accélérer l'adoption d'une stratégie
nationale d'investissement. Il est également primordial de formaliser les
engagements des secteurs privé et bancaire concernant la mise en œuvre
des dispositions de la charte nationale d'investissement. De plus, la mise
en place d'un observatoire national de l'investissement est nécessaire pour
renforcer le suivi et le pilotage des réalisations chiffrées au regard des
objectifs stratégiques. Il convient aussi de compléter les dispositifs de
soutien à l'investissement, notamment en adoptant les textes
réglementaires relatifs à la mise en œuvre du dispositif spécial dédié aux
très petites, petites et moyennes entreprises, afin d'assurer une application
cohérente et intégrée de cette réforme.
La simplification et la digitalisation des procédures, ainsi que la facilitation
de l'accès au foncier, tout comme l'aboutissement de la mise en œuvre de
la charte de déconcentration administrative, constituent des leviers
essentiels pour stimuler l'investissement privé et accroître sa contribution
dans l’investissement total avec l'objectif de la doubler à l'avenir.
En ce qui concerne la réforme de l'administration publique, qui constitue
un pilier fondamental pour améliorer ses prestations aux usagers,
notamment les investisseurs, ainsi que pour instaurer les règles de
transparence et de bonne gouvernance, les efforts de simplification des
démarches et procédures administratives n'ont toujours pas atteint leurs
principaux objectifs, malgré l'entrée en vigueur de la loi sur la
simplification des procédures et formalités administratives depuis plus de
quatre ans. Ceci est dû essentiellement aux insuffisances constatées en
matière de suivi, par certains départements ministériels et établissements
publics, du processus de codification et de publication des décisions
administratives qui relèvent de leur domaine de compétence, à l’absence
d'un plan de gestion du changement et d'accompagnement des




                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              13
     transformations structurelles liées à la réforme administrative, ainsi qu’au
     retard dans la simplification des parcours des usagers.
     Dans le même contexte, le chantier de la transformation digitale peine à
     avancer, comme en témoigne la faible mise en œuvre des programmes
     numériques. Bien que le nombre de services publics digitalisés ait atteint
     605 à fin 2023, cette évolution n'a pas eu d'impact significatif sur la
     simplification des procédures administratives pour les usagers, surtout que
     le pourcentage de services complètement digitalisés ne dépasse pas 23%
     du total des services offerts, et ce en raison des contraintes législatives,
     réglementaires et managériales que connaît la digitalisation des services
     publics, en plus des insuffisances des mécanismes de planification adoptés
     pour gérer la transition numérique.
     Dans le domaine de l’habitat, et face à un taux d'urbanisation de plus en
     plus élevé, actuellement de près de 62,8%, le programme de la création de
     quatre nouvelles villes a été lancé depuis 2004, afin de réduire la pression
     sur les grandes agglomérations, de stimuler la dynamique territoriale et de
     relever les défis liés à la croissance démographique et spatiale. Cependant,
     les indicateurs actuels de ce programme révèlent des résultats limités
     puisque la population de ces villes ne représente que 17% de l'objectif fixé,
     tandis que le taux de réalisation des unités d'habitation n'atteint que 20%
     des prévisions initiales. De plus, le niveau d'achèvement des équipements
     publics ne dépasse pas 26%, alors qu’environ 58% des investissements
     prévus ont été réalisés.
     Cette situation résulte, en plus de l'absence d'un cadre juridique pour les
     villes nouvelles, de l'incohérence des initiatives publiques portant sur leur
     création, qui ne s'alignent pas avec les orientations des documents
     d'urbanisme et d'aménagement du territoire national. Elle est également
     due à l'absence d'études préalables de faisabilité sociale et économique, au
     manque de coordination entre les approches sectorielles, ainsi qu'à un
     engagement limité dans la réalisation des équipements publics. S’ajoutent
     à cela le manque de contrôle des processus d'urbanisation autour des
     nouvelles villes, ainsi que la défaillance du partenariat avec le secteur privé
     pour atteindre les objectifs fixés, comme en témoigne la résiliation de 52%
     des conventions conclues entre l'État et les acteurs privés dans ce cadre.
     Pour surmonter les obstacles entravant l'atteinte des objectifs de création
     des villes nouvelles, il est nécessaire d'ériger le pilotage de ces projets à un
     niveau stratégique garantissant la cohérence des interventions, la
     convergence et la coordination efficace entre les différentes parties
     prenantes. Il convient également d'élaborer un plan de réhabilitation pour
     ces quatre nouvelles villes, intégrant une vision globale de leur
     développement. Ce plan devrait inclure les aspects liés à l'intégration


        Rapport annuel de la Cour des comptes au titre de 2023-2024
14                    - Principaux axes -
territoriale, au rôle fonctionnel, à la mobilité urbaine, à la disponibilité
d'infrastructures et d'équipements, ainsi qu'à la maintenance. L'ensemble
de ces actions devra s'inscrire dans le cadre d'un contrat entre l'État, les
collectivités territoriales et les acteurs publics responsables de l'exécution
de ce plan de réhabilitation, en précisant les engagements financiers de
chaque partie.

Majesté,
La finalité de la création des institutions supérieures de contrôle,
conformément aux normes internationales, est de participer à la création
de la différence dans la vie des citoyens à travers le renforcement de la
reddition des comptes, de la transparence et de l’intégrité du secteur public.
Les travaux, à forte valeur ajoutée, tiennent compte des défis internes et
externes dans leurs réponses aux attentes des parties prenantes et aux
préoccupations des citoyens.
L'objectif principal que les institutions supérieures de contrôle doivent
s'efforcer d'atteindre, en collaboration avec les autres intervenant publics,
consiste à servir le citoyen et lui assurer des prestations publiques qui
préservent sa dignité.
En raison de la diversité de leurs missions, combinant les aspects de
contrôle, d’audit, d’évaluation et, le cas échéant, de sanction des
infractions, la Cour et les Cours régionales des comptes veillent à exercer
leurs missions selon une approche intégrée et équilibrée, appuyée par la
mise en œuvre de passerelles entre ces divers domaines de compétences.
Cette démarche renforce l’impact des travaux des juridictions financières,
y compris en matière de contribution à la moralisation de la vie publique
et de lutte contre la corruption.
Les missions menées dans le cadre des attributions extra-juridictionnelles,
notamment le contrôle de la gestion et l’évaluation des programmes et
projets publics, constituent un point de départ pour engager la
responsabilité des gestionnaires publics, que ce soit dans le cadre de la
procédure disciplinaire administrative, de la procédure de la discipline
budgétaire et financière ou de la procédure pénale. Dans ce contexte,
l'exercice par les juridictions financières de leurs attributions
juridictionnelles contribue, quant à lui, de manière significative à
l’identification des risques afférents à la gestion de la chose publique. Sur
la base de ces éléments, des missions de contrôle ou d'évaluation sont
programmées pour mettre en évidence les causes sous-jacentes de ces
risques et leurs répercussions sur la gestion ainsi que pour formuler des
recommandations ciblées afin d’y remédier.



                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              15
     À cet égard, les juridictions financières, dans le cadre d'une approche
     intégrée du contrôle visant à établir une complémentarité entre l’ensemble
     de leurs attributions, veillent à exploiter de manière optimale les divers
     comptes, documents et situations financières et comptables produits,
     notamment par les comptables publics. Elles s'efforcent de dépasser la
     perception limitant la fonction de ces comptes à servir uniquement de base
     pour rendre des jugements et arrêts dans le domaine de la vérification et du
     jugement des comptes, en les considérant également comme un mécanisme
     essentiel pour engager la responsabilité des différents acteurs impliqués
     dans la gestion des fonds publics.
     À travers cette approche, et eu égard à ses missions de consolidation des
     valeurs de bonne gouvernance, de transparence et de reddition des
     comptes, ainsi que de préservation du caractère sacré des fonds publics, la
     Cour veille à exercer de manière équilibrée son rôle de contrôle et, le cas
     échéant, son rôle répressif. Parallèlement, elle s'assure que ses travaux
     contribuent à la prévention et à l'anticipation des risques en alertant sur les
     défaillances structurelles et organisationnelles affectant la gestion de la
     chose publique.
     L’engagement des poursuites et la mise en cause de la responsabilité des
     gestionnaires publics n’est pas une fin en soi, mais, plutôt, un mécanisme
     important pour moraliser la vie publique, chose que les juridictions
     financières s'efforcent de mettre en œuvre. La finalité ultime est
     d'améliorer la gestion publique et d'anticiper les risques qui affectent la
     performance des services publics, entraînant des pertes et des dommages
     considérables, non seulement au niveau financier mais également aux
     niveaux économique, social et environnemental, qui sont tout aussi
     cruciaux.
     Les juridictions financières sont tenues, lorsqu'elles constatent des
     dysfonctionnements et une mauvaise gestion des fonds publics, ainsi que
     le non-respect des règles régissant cette gestion, de prendre toutes les
     mesures légales nécessaires et de déclencher les procédures en vigueur.
     Elles doivent également mener des investigations pour identifier les causes
     profondes de ces manquements et les circonstances y afférentes. Dans ce
     cheminement, elles tiennent compte des complexités qui caractérisent
     désormais le processus de prise de décision publique, dans un contexte
     marqué par l'incertitude. Elles doivent attirer l'attention, le cas échéant, sur
     ces défaillances et leurs causes, dans le cadre d'une approche globale visant
     à les anticiper, les éviter et à en éradiquer les causes.
     La prise en compte de tous ces aspects s'inscrit dans le cadre d’une
     perspective novatrice visant à revoir le système de responsabilité des
     gestionnaires publics. Cela implique une reconsidération des rôles du juge


        Rapport annuel de la Cour des comptes au titre de 2023-2024
16                    - Principaux axes -
financier de manière à répondre à la finalité de la création des juridictions
financières. L’objectif est également de renforcer leur rôle dans la
consécration des normes d'utilisation rationnelle des ressources publiques,
conformément aux lois en vigueur, tout en contribuant à la prise de
décision, notamment face aux enjeux et défis auxquels notre pays est
confronté.
Le présent document relate les plus importantes thématiques contenues
dans le rapport annuel de la Cour des comptes au titre de 2023-2024,
présenté à Votre Majesté. Il comprend des chapitres dédiés aux
attributions juridictionnelles (discipline budgétaire et financière,
vérification et jugement des comptes), au contrôle et suivi des déclarations
de patrimoine, ainsi qu’à l’audit des comptes annuels des partis politiques.
Il comprend, également, des chapitres relatifs au suivi de la mise œuvre
des grands chantiers de réformes (eau, régionalisation avancée, protection
sociale, investissement, établissements et entreprises publics et système
fiscal,), et à l’évaluation des programmes et projets publics, au contrôle de
la gestion, ainsi qu’au suivi de la mise en œuvre des recommandations.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              17
     Rapport annuel de la Cour des comptes au titre de 2023-2024
18                 - Principaux axes -
                    Mentions importantes
▪   Les axes principaux, objet du présent document, ont été préparés sur
    la base du rapport annuel de la Cour des Comptes 2023-2024, élaboré
    en application des dispositions de l’article 148 de la Constitution, et
    conformément à l'approche adoptée dans le cadre des orientations
    stratégiques des juridictions financières pour la période 2022-2026, et
    en tenant compte des dispositions de la loi n° 62.99 formant code des
    juridictions financières relatives à l'élaboration de ce rapport annuel
    et à son approbation, notamment ses articles 22, 99 et 100;
▪   Les travaux objet de ces axes s'inscrivent dans le cadre de l’exécution
    du programme annuel 2023. Eu égard aux délais requis par les
    procédures en vigueur, et afin de garantir l'actualité des résultats de
    ces travaux et tenant compte des réponses des organismes soumis au
    contrôle, les statistiques et les données ont été mises à jour jusqu'à fin
    septembre 2024, sauf indication contraire ;
▪   Ces axes principaux présentent une synthèse des résultats les plus
    saillants des travaux de la Cour et des Cours Régionales des Comptes,
    notamment ceux en relation avec la consécration du principe de la
    reddition des comptes (activités juridictionnelles, déclaration
    obligatoire du patrimoine, audit des comptes des partis politiques et
    de l’emploi du soutien annuel supplémentaire à ces partis), ainsi que
    ceux afférents à l’amélioration de la performance de la gestion
    publique (suivi des chantiers des grandes réformes, évaluation des
    programmes et des projets publics, contrôle de la gestion, suivi de la
    mise en œuvre des recommandations) ;
▪   S’agissant des travaux relatifs au suivi des chantiers des grandes
    réformes, à l'évaluation des programmes et projets publics, au contrôle
    de la gestion, les axes principaux comprennent les observations les
    plus importantes relevées par les juridictions financières et les
    principales recommandations émises par celles-ci, en tenant compte
    des réponses des organismes concernés par les missions objet de ces
    travaux ;
▪   Ces axes principaux ont été préparés en langue arabe, puis traduis en
    langue française ;
▪   Les principaux axes du rapport annuel, disponibles en arabe et en
    français, sont téléchargeables sur le site officiel de la Cour des
    comptes : www.courdescomptes.ma;
▪   Pour plus de détail sur les résultats des différents travaux des
    juridictions financières, le rapport annuel de la Cour des comptes est
    accessible sur son site officiel précité.


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              19
     Rapport annuel de la Cour des comptes au titre de 2023-2024
20                 - Principaux axes -
               Activités juridictionnelles
Conformément aux dispositions de la loi 62.99 formant code des
juridictions financières, la Cour et les Cours régionales des comptes (CRC)
exercent, outre les compétences de contrôle et d’évaluation, des
compétences juridictionnelles en matière de vérification et de jugement des
comptes produits par les comptables publics et par les comptables de fait
ainsi qu’en matière de discipline budgétaire et financière (DBF) suite aux
décisions de poursuite établies par le parquet général près les juridictions
financières.
Les principales conclusions des activités juridictionnelles de janvier 2023
au 30 septembre 2024, sont comme suit.
      1. Travaux en matière de discipline budgétaire et financière :
         Exercice optimisé par la prise de mesures correctives à
         caractère préventif et par la mise en œuvre d’une politique
         de poursuite coordonnée avec le parquet général près les
         juridictions financières
Suite aux observations soulevées par les juridictions financières dans le
cadre des missions de contrôle de la gestion et d'évaluation, en particulier
celles susceptibles de donner lieu à des procédures, parfois coûteuses, de
poursuites en matière de DBF ou des actions disciplinaires administratives
ou pénales, il a été noté qu'un certain nombre d'organismes ont pris de
manière proactive des mesures correctives dont l’impact s’est avéré positif
aussi bien sur le plan financier que sur les plans managérial,
environnemental et social. Cet impact a porté sur le recouvrement de
créances et droits dus (54 MDH), le respect d’engagements contractuels
(78 MDH), l’application de pénalités de retard (6,3 MDH), la restitution de
montants payés indument (0,82 MDH), en plus de l’engagement de
procédures de recouvrement de créances pour un montant global d'environ
52 MDH.
Il a été noté que des mesures ont également été prises afin de renforcer les
mécanismes de contrôle interne et d’en ancrer les principes et les bases,
condition indispensable pour l’amélioration de la gestion et la prévention
contre les cas de corruption financière et administrative.
De même, le processus de préparation des projets de saisines en matière de
discipline budgétaire et financière, tient compte de la politique de poursuite
établie en coordination avec le parquet général près d’elles. Le coût de la
procédure est ainsi apprécié et comparé aux enjeux financiers concernés
par les projets de saisines. Une évaluation est aussi faite de l’efficacité de
la procédure à redresser les défaillances relevées, comparée aux autres


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              21
     moyens dont disposent les juridictions financières en vertu de la loi, tels
     que l'émission de recommandations, de référés, de lettres aux responsables
     des organismes concernés ou l’exercice de l’action disciplinaire , via le
     parquet général près les juridictions financières, pour les faits de nature à
     justifier une sanction administrative ou la prise de mesures correctives
     pendant les missions de contrôle.
     En ce qui concerne les dossiers en cours en matière de DBF, leur
     nombre s’est élevé, pendant la période sus visée, à un total de 297 dossiers,
     dont 86 ont été jugés en statuant par des amendes d’un total de
     5.056.500,00 DH et par des jugements de remboursements de sommes au
     titre de pertes subies par les organismes concernés d’un montant de
     9.148.973,42 DH.
     S’agissant de l’origine des saisines, et comme c'est le cas depuis l'entrée en
     vigueur du code des juridictions financières, et compte tenu des autorités
     habilitées à saisir la Cour en matière de DBF, 92 % des affaires en cours
     ont eu comme origine de saisine des instances délibérantes internes à la
     Cour.
     Au niveau des CRC, les saisines externes, émanant toutes du ministère de
     l'Intérieur ont été à l’origine de 21% des saisines enregistrées. Les
     instances internes des CRC ont été, pour leur part, à l’origine de 79% des
     affaires portées devant lesdites CRC. Il est à souligner que 36 nouveaux
     projets de saisines internes ont été adressés au parquet général près les
     juridictions financières.
     En ce qui concerne les catégories d’organismes et de personnes
     poursuivies dans le cadre des dossiers en cours, il y a lieu de noter que les
     établissements publics ont représenté 75 % des organismes objets de
     saisines devant la Cour (3 universités, 3 chambres professionnelles et 3
     autres établissements), tandis que les services de l’Etat ont fait l’objet de
     25 % des saisines (direction centrale, service déconcentré et service de
     l’Etat géré de manière autonome).
     La répartition des personnes poursuivies, devant la Cour, par catégorie fait
     ressortir que les ordonnateurs et les sous ordonnateurs en forment 52 %
     (directeurs généraux d’établissements publics et des entreprises affiliées à
     l'un de ces établissements, directeurs centraux et responsables de services
     déconcentrés des ministères), les niveaux fonctionnels exécutifs
     constituent 20 % des personnes poursuivies (chefs de Divisions et de
     Services) et les fonctionnaires et agents publics en représentent 28 %.
     Au niveau des CRC, les affaires de DBF ont concerné 110 organismes dont
     principalement les communes à hauteur de 93 % (103 communes), suivies
     par les Provinces pour 3 % des cas de saisine (trois provinces), puis par



        Rapport annuel de la Cour des comptes au titre de 2023-2024
22                    - Principaux axes -
deux régions et deux groupements de collectivités territoriales constituant
chacune 2 % des organismes objets de saisine.
Le nombre de personnes poursuivies devant les CRC, dans le cadre de ces
affaires, a atteint 253 personnes réparties entre 122 présidents de conseils
locaux actuels et sortants (collectivités territoriales et établissements
publics locaux) soit 48% du total de personnes poursuivies, 62
fonctionnaires et techniciens (24 %) et 28 % pour le reste englobant des
régisseurs de recettes, des chefs de services, des vice-présidents de conseils
locaux, des directeurs, des chefs de divisions et des membres de conseils
communaux.
Les faits constituant des présomptions d’infractions dans le cadre des
dossiers en cours de DBF, ont concerné principalement les domaines de la
gestion des marchés publics et des recettes.
Ainsi, la plupart des faits soulevés concernant les marchés publics portent
sur le non-recours injustifié à la concurrence, la non application correcte
des critères d’évaluation des offres spécifiés dans le règlement de
consultation, la non détermination précise des besoins à satisfaire par la
commande lors de l'établissement du cahier des prescriptions spéciales. Ils
portent, également, sur la certification inexacte du service fait pour des
travaux ou de fournitures réalisés en deçà des quantités visées dans les
décomptes ou non conformes aux prescriptions techniques établies par les
clauses contractuelles, la réception provisoire de travaux inachevés ou de
qualité insuffisante, et la non-mise en œuvre des sanctions prévues par les
marchés conclus en cas de défaillances ou de retard dans leur exécution.
Pour la gestion des recettes, les faits relevés concernent, notamment, des
insuffisances en matière d’appréhension et de détermination de l’assiette
fiscale, le non recours à la taxation d’office pour défaut de déclaration par
le redevable, le manque de contrôle des déclarations déposées, et enfin, des
manquements au niveau du recouvrement de taxes ou de la liquidation du
montant dû à leur titre.
      2. Travaux en matière de vérification, d’instruction et de
         jugement des comptes : Efficacité du contrôle de validité des
         dépenses impactée par les modifications apportées au régime
         de responsabilité du comptable public et par la mise en place
         de systèmes informatiques encadrant le processus
         d’exécution des dépenses
Dans le cadre de l’exercice de leur attribution relative à la vérification,
l’instruction et le jugement des comptes, les juridictions financières ont
noté le reversement par les comptables publics de sommes s’élevant à
28.179.276,08 DH aux organismes publics concernés suite à la notification
qui leur a été faite de notes d’observations et d’arrêts et jugements


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              23
     provisoires, bien avant qu’elles ne statuent définitivement sur les comptes
     concernés.
     S’agissant des arrêts et jugements rendus par les juridictions financières,
     celles-ci ont prononcé des débets d’un montant global d’environ 54,8
     MDH et des quitus dans 81 % des arrêts et jugements émis.
     Le montant des débets dus à l’absence de diligences que le comptable
     public doit faire en matière de recouvrement des recettes a constitué 89%
     des débets prononcés, tandis que les débets liés aux manquements à
     l’occasion de l’exercice du contrôle de validité de la dépense qu’il est tenu
     d’effectuer en vertu des lois et règlements en vigueur, n'ont représenté que
     11% du montant total des débets, répartis entre débets résultant de
     manquements en matière de contrôle de l’exactitude des calculs de
     liquidation (9%), ceux liés au non-respect du caractère libératoire du
     règlement (1%) et de débets à cause de l’absence du visa préalable (1%).
     Les modifications apportées au régime de responsabilité personnelle et
     pécuniaire des comptables publics, notamment par les lois de finances de
     2005 et de 2008, ont restreint l’étendue du contrôle du juge des comptes
     après avoir limité le champ de responsabilité du comptable public en matière
     de validité de la dépense au contrôle des calculs de liquidation, du caractère
     libératoire du règlement et de l’existence du visa préalable alors qu’il portait
     auparavant aussi sur la justification du service fait et le respect des règles de
     prescription et de déchéance. Ces modifications expliquent, entre autres
     facteurs, le taux élevé des jugements et arrêts de quitus et la faiblesse relative
     des débets prononcés liés aux manquements dans l’exercice du contrôle de
     validité de la dépense que le comptable public est tenu d’effectuer. D’autres
     facteurs y ont contribué également, notamment la mise en place de systèmes
     informatiques encadrant le processus d’exécution des dépenses, en
     particulier le système de gestion intégrée de la dépense (GID) et l’effet
     pédagogique inhérent aux arrêts publiés par la Cour.
     Ces évolutions requièrent une reconsidération du système de responsabilité
     en vigueur et de la procédure de vérification, d’instruction et de jugement
     des comptes, compte tenu notamment de la longueur de cette procédure et
     de son coût comparé à ses résultats, notamment en matière de contrôle des
     dépenses.
             3. Déféré des affaires à caractère pénal : 16 dossiers entre
                janvier 2023 et fin septembre 2024
     Conformément aux articles 111 et 162 du code des JF, le Procureur Général
     du Roi près la Cour des comptes a déféré au Procureur Général du Roi près
     la Cour de cassation, Président du Ministère public, 16 dossiers portant sur
     des présomptions à caractère pénal afin qu’il prenne les mesures qu'il
     estime appropriées à leur égard selon les procédures en vigueur.


        Rapport annuel de la Cour des comptes au titre de 2023-2024
24                    - Principaux axes -
   Déclaration obligatoire de patrimoine
Le nombre de déclarations de patrimoine déposées du 1er janvier 2023 au
30 septembre 2024, au niveau des juridictions financières, s’est établi à
15.876, dont 1.239 déposées à la Cour des comptes et 14.637 déposées aux
Cours régionales des comptes.
Les déclarations des fonctionnaires et agents publics constituent 89% des
déclarations déposées à la Cour, tandis que celles des élus des collectivités
territoriales représentent 65% des déclarations déposées aux Cours des
comptes régionales, étant donné que la campagne de renouvellement des
déclarations des élus locaux, requis par la loi tous les deux, a eu lieu en
février 2024.
Ainsi, le total des déclarations déposées depuis 2010 au 30 septembre 2024
est porté à 462.826 déclarations, réparties entre 398.792 déclarations pour
la catégorie des fonctionnaires et agents publics (86,2%), 57.964
déclarations pour la catégorie des élus des conseils des collectivités
territoriales et des chambres professionnelles (12,5%) et 6.070 déclarations
pour les autres catégories d’assujettis (1,3%).
       1. Amélioration de la situation déclarative des assujettis non
          déclarants suite à la mise en œuvre de la procédure de mise
          en demeure
Les juridictions financières ont continué, durant les années 2023 et 2024,
à suivre les régularisations de la situation déclarative des assujettis non
déclarants suite à la mise en œuvre de la procédure de mise en demeure à
leur égard. Ainsi, 214 sur 860 assujettis ayant accusé réception des mises
en demeure, de la catégorie des fonctionnaires et agents publics, ont déposé
leurs déclarations de patrimoine, soit un taux de régularisation de 24,8%.
Toutefois, il importe de souligner que les mesures de notification des mises
en demeure adressées à 1.116 assujettis défaillants, ont révélé que 256
d’entre eux étaient en cessation de fonctions avant 2019, à savoir l'année
de mise en place de la plateforme électronique dédiée au suivi des
déclarations déposées et à l’arrêt des listes des assujettis ayant failli à leurs
obligations déclaratives. Ces données confirment à nouveau, les
insuffisances notées par la Cour, en matière d’actualisation des listes des
assujettis chargées dans la plateforme par les autorités gouvernementales,
ce qui porte atteinte à l’efficacité de la mission de suivi des mises en
demeure et au caractère actuel des données sur lesquelles elle se base.
Concernant les élus territoriaux, le suivi des mises en demeure pour un
total de 899 élus défaillants notifiés, a révélé que 59 sur 75 élus défaillants


                                            Rapport annuel de la cour des comptes au titre de 2023-2024
                                                         - Principaux axes -                              25
     ont régularisé leur situation déclarative, soit 79%, alors que seulement 67
     sur 824 élus, en situation de cessation de mandat, ont déposé leurs
     déclarations. À cet égard, les Cours régionales des comptes engagent la
     procédure de sanctions prévue par la loi à l’encontre des assujettis qui
     refusent de régulariser leur situation déclarative, en dépit de l’expiration
     du délai de soixante jours à compter de la date de notification des mises en
     demeure.
     De même, les juridictions financières prennent les mesures nécessaires en
     vue d’assurer la notification des mises en demeure aux assujettis défaillants
     qui n’en ont pas encore accusé réception.
             2. Référé du Premier Président de la Cour des comptes relatif
                aux « voies d’amélioration du système de la déclaration
                obligatoire du patrimoine »
     La Cour avait réalisé une étude évaluative de l’exercice de ses attributions
     en matière de réception, de suivi et de contrôle des déclarations du
     patrimoine depuis l’entrée en vigueur, au mois de février 2010, du
     dispositif de déclaration obligatoire du patrimoine. Les conclusions de
     cette étude ont notamment mis en lumière l’urgence de remédier à un
     certain nombre d’insuffisances ; et en application des dispositions du Code
     des juridictions financières, la Cour a adressé en juillet 2024, un référé dans
     ce sens au Ministère délégué auprès du Chef du Gouvernement, chargé de
     la transition numérique et de la réforme administrative.
     Ce référé est axé sur les voies d’amélioration du système juridique
     régissant la déclaration obligatoire du patrimoine, afin de remédier aux
     insuffisances relevées et le renforcer par des dispositions à même de lui
     permettre de contribuer plus efficacement à la prévention et à la lutte contre
     la corruption.
     Tout en prenant acte de l’interaction positive du Ministère délégué chargé
     de la transition numérique et de la réforme administrative dans sa réponse
     aux observations et recommandations objet dudit référé, la Cour souligne
     la nécessité d’élaborer un système juridique unifié et global, intégrant les
     différentes catégories de personnes assujetties à la déclaration obligatoire
     du patrimoine et de se conformer à cet égard aux dispositions de la
     Constitution de 2011, notamment ses articles 147 et 158. La Cour insiste,
     également, sur l’importance d’assurer les conditions à même de dépasser
     les difficultés constatées dans le processus d’établissement des listes des
     assujettis et de mettre en place une procédure pour les arrêter et les
     actualiser et fixer le délai limite de leur chargement sur la plateforme
     électronique dédiée au suivi des déclarations de patrimoine.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
26                    - Principaux axes -
Par ailleurs, le référé recommande la refonte du contenu du modèle actuel
de déclaration de patrimoine, la mise en place d’un système électronique
intégré de réception, de suivi et de contrôle des déclarations du patrimoine,
ainsi que la mise en place d’un régime approprié et progressif de sanctions
en cas d’infractions ou de manquements liés à la déclaration du patrimoine.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              27
       Audit des comptes des partis politiques
         et de l’emploi du soutien annuel
                   supplémentaire
     Dans le cadre de ses attributions constitutionnelles, la Cour des comptes a
     publié, le 28 février 2024, un rapport détaillé relatif à l’audit des comptes
     des partis politiques et à la vérification de la sincérité de leurs dépenses au
     titre du soutien public de l’année 2022. Ce rapport a également été
     communiqué au Ministère de l'Intérieur.
             1. Soutien accordé aux formations politiques et syndicales :
                restitution d’un montant de 38,40 MDH jusqu’en novembre
                2024
     Au 13 novembre 2024, 24 partis politiques et une organisation syndicale
     ont restitué au Trésor 38,40 MDH au titre du soutien annuel ou de la
     participation de l’État au financement des campagnes électorales non
     justifiés ou non utilisés. Le montant qui reste à restituer, dans ce cadre, est
     arrêté à 22 MDH, dû par 13 partis et deux (2) organisations syndicales.
     Au vu de ce qui précède, la Cour a recommandé au Ministère de
     l'Intérieur et aux formations politiques et syndicales de poursuivre les
     efforts pour la restitution au Trésor des montants de soutien indus, non
     utilisés ou non justifiés. La Cour a également recommandé au Ministère de
     l’Intérieur d’accompagner les partis en organisant des formations
     périodiques au profit de leurs cadres chargés de la gestion financière,
     comptable et administrative.
             2. Soutien annuel supplémentaire : Nécessité d'adapter et de
                compléter les textes réglementaires
     Concernant le soutien annuel supplémentaire accordé aux partis pour
     couvrir leurs dépenses liées aux missions, études et recherches au titre de
     l’année 2022, sept (7) partis ont bénéficié d’un montant total de 20,10
     MDH, entre septembre et novembre 2022. Toutefois, en raison du court
     délai entre la date d’octroi de ce soutien (entre septembre et novembre
     2022) et la date limite de dépôt des comptes d’emploi (fin décembre 2022),
     il n'a pas été possible pour les partis bénéficiaires de respecter ce délai.
     Deux partis ont ainsi restitué le montant total du soutien dont ils ont
     bénéficié en raison de sa non-utilisation (2,76 MDH).
     À cet égard, la Cour a soulevé la nécessité d’harmoniser les dispositions
     du décret relatif aux modalités de répartition et de versement du soutien
     aux partis politiques avec celles de la loi organique relative aux partis


        Rapport annuel de la Cour des comptes au titre de 2023-2024
28                    - Principaux axes -
politiques et de la loi relative au code des juridictions financières. En effet,
des dispositions non adaptées ont été intégrées dans le décret précité, liant
l’octroi du soutien annuel supplémentaire l’année suivante à la
«déclaration préalable par la Cour de la conformité » de l’emploi du soutien
versé au parti aux fins auxquelles il a été accordé l’année précédente.
Au vu de ce qui précède, la Cour a recommandé au Chef du
Gouvernement et au Ministère de l’Intérieur d’harmoniser les
dispositions du décret fixant les modalités de répartition du soutien accordé
aux partis politiques et les modalités de son versement avec les dispositions
de la loi organique relative aux partis politiques et du code des juridictions
financières.
      3. Examen des comptes de campagnes électorales : Envoi au
         ministre de l’intérieur de la liste des candidats n’ayant pas
         déposé les comptes de leurs campagnes électorales et saisine
         des tribunaux administratifs compétents
Suite à l’approbation des rapports relatifs à l'examen des comptes des
campagnes électorales des candidats aux élections de l'année 2021 et leur
publication en date du 8 juin 2023, la Cour des comptes a saisi les tribunaux
administratifs compétents pour prononcer l’annulation de l’élection des
candidats aux élections des conseils des collectivités territoriales qui n'ont
pas produit leurs comptes de campagne (21 élus), et ce, en application des
dispositions de l’article 159 de la loi organique relative à l'élection des
membres des conseils des collectivités territoriales. Elle a également
adressé au Ministre de l’Intérieur la liste des candidats qui n’ont pas déposé
les comptes de leurs campagnes électorales (474 candidats) pour prononcer
leur inéligibilité aux élections législatives générales et partielles ainsi
qu'aux élections des conseils des collectivités territoriales et des chambres
professionnelles pour deux mandats successifs, et ce, en application des
dispositions des articles 96, 97 et 158 des lois organiques relatives,
respectivement, à la Chambre des représentants, à la Chambre des
conseillers et à l'élection des membres des conseils des collectivités
territoriales.


.




                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              29
                    Suivi des chantiers des grandes
                               réformes
     Dans le cadre du suivi qu’elle effectue sur la mise en œuvre des chantiers
     des grandes réformes, la Cour des comptes a procédé à une appréciation de
     l’état des actions réalisées et celles en cours, et a identifié les risques
     pouvant entraver l’atteinte des objectifs assignés à ces chantiers.


                                              Secteur de l'eau :
       Défis liés à l’accélération de la mise en œuvre des grands
       chantiers pour faire face aux risques du stress hydrique

     La problématique du stress hydrique constitue un des défis majeurs
     auxquels fait face notre pays, notamment avec l’accentuation des effets du
     changement climatique et la succession des années de sécheresse. Pour
     atténuer l’impact de la crise hydrique, notamment en ce qui concerne la
     sécurisation de l'approvisionnement en eau potable et la satisfaction des
     besoins     des    secteurs     productifs, le    programme       national
     d’approvisionnement en eau potable et d’irrigation 2020-2027 (PNAEPI)
     a été lancé début 2020.
     Le PNAEPI a démarré avec un budget global du de 115 MMDH. Afin de
     garantir la réalisation de l’ensemble de ses projets et l’atteinte des objectifs
     fixés, ce budget a été porté à 143 MMDH, trois ans après son lancement.
     Le Programme englobe le développement de l’offre en eau à travers
     l’accélération de la construction des barrages, le renforcement et la
     sécurisation de l’approvisionnement en eau potable, le dessalement de
     l’eau et l’interconnexion des bassins hydrauliques (83,9 MMDH), le
     renforcement de l’alimentation en eau potable en milieu rural
     (28,3 MMDH), la gestion de la demande et la valorisation de l’eau,
     notamment par l’économie d’eau d’irrigation et l'amélioration du
     rendement des réseaux d’adduction et de distribution de l'eau potable
     (27,5 MMDH), ainsi que la réutilisation des eaux usées traitées
     (3 MMDH).
     S’agissant de la construction des barrages, le PNAEPI prévoit la
     construction de 21 grands barrages et 330 petits barrages. Dans ce sens,
     avec la mise en service d’un ensemble de barrages, dont la construction a
     commencé avant le lancement du programme, notamment les barrages
     Todgha (province de Tinghir), Tiddas (province de Khemisset), et Agdz
     (province de Zagora) et Fask (province de Guelmim), la capacité totale de
     stockage est passée de 18,7 milliards de m³ en 2020 à 20,7 milliards de m³


        Rapport annuel de la Cour des comptes au titre de 2023-2024
30                    - Principaux axes -
fin 2023. En outre, il est prévu, selon les données du ministère de
l'Equipement et de l'Eau, que cette capacité augmente pour atteindre 24
milliards de m3 à fin 2027, soit une augmentation de 20%.
Il convient de noter que certains projets de grands barrages dont la
réalisation avait commencé avant le lancement du PNAEPI 2020-2027 ont
enregistré du retard par rapport aux prévisions, notamment les barrages de
M’dez (province de Sefrou), Targa Ou Madi (province de Guercif), ainsi
que le projet de reconstruction du barrage Sakia El Hamra (province
Laâyoune). Ce retard est dû principalement aux résiliations des marchés de
travaux les concernant. Il est à signaler que de nouveaux marchés
d’achèvement ont été lancés pour ces projets, et que le barrage de M’dez a
été mis en eau en février 2024 et l’achèvement des deux autres barrages est
prévu pour 2026.
Concernant la gestion de la demande et la valorisation de l’eau, la
superficie équipée en systèmes d’irrigation localisée a atteint environ
794.000 hectares à fin 2023, représentant près de 50% de la superficie
irriguée à l’échelle nationale, contre 43% en 2020 et seulement 9% en
2008.Toutefois, les efforts déployés, pour moderniser les réseaux
d’irrigation collective et promouvoir l’irrigation localisée n’ont pas permis
de stabiliser la demande en eau d’irrigation, sachant que le problème de la
surexploitation des eaux souterraines s'est aggravé.
Par ailleurs, pour combler le déficit en ressources hydriques, le
dessalement des eaux de mer qui s’impose, a pour objectif de mobiliser
1,4 milliard de m³ d’eau par an à l’horizon 2027. Le nombre de stations de
dessalement est passé de huit stations, d’une capacité totale de production
de 46 millions de m³ par an, avant le lancement du PNAEPI, à 15 stations
en 2024, d’une capacité totale de production à 192 millions de m³ par an.
En outre, six grands projets de dessalement sont en cours de réalisation,
avec une capacité totale de 438,3 millions de m³ par an, dont la station de
Casablanca d’une capacité de 300 millions de m³ par an.
Par ailleurs, le PNAEPI prévoit la réutilisation de 100 millions de m³
d’eaux usées traitées par an à l’horizon 2027, sachant que ce volume a
atteint environ 37 millions de m³ en 2023. Néanmoins, la réutilisation des
eaux usées traitées reste limitée aux secteurs industriels et à l’arrosage des
espaces verts, alors que son usage dans l’agriculture demeure insignifiant
en raison de l'absence de dispositifs institutionnels et juridiques encadrant
le partage des coûts entre les gestionnaires des stations de traitement et les
agriculteurs, ainsi que du manque de normes fixant la qualité des eaux
usées à réutiliser en agriculture.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              31
     S’agissant de l’interconnexion des bassins hydrauliques, le projet
     d’interconnexion des bassins de Sebou et de Bouregreg, d’un coût de
     6 MMDH, a été achevé et mis en service fin août 2023. Ce projet fait partie
     de la première phase du programme d’interconnexion des bassins de
     Sebou, Bouregreg et Oum Er-Rbia, dont le lancement des phases suivantes
     est prévu en 2024.
     De plus, le projet d’interconnexion des barrages Oued El Makhazine et Dar
     Khrofa est également en cours d’achèvement, six mois après son
     lancement. Ce projet, d’un coût de 840 MDH, vise à sécuriser les besoins
     en eau potable du Grand Tanger et à alimenter en eau d’irrigation le
     périmètre de Dar Khrofa, d’une superficie de 21.000 hectares.
     En ce qui concerne les risques auxquels peut être confrontée l’atteinte des
     objectifs de la politique de l’eau de notre pays, il y a lieu de citer
     l’aggravation de la situation hydrique due à une accentuation du
     changement climatique, le retard des projets de dessalement, de
     reconversion à l’irrigation localisée, d’interconnexion des bassins
     hydrauliques, et des projets de barrages, en particulier dans les zones à forte
     pluviométrie.
     Parmi ces risques, il y a également celui relatif au retard de réalisation du
     projet de liaison électrique pour le transport de l’énergie renouvelable du
     sud du pays vers le centre et le nord afin d’alimenter les stations de
     dessalement en énergie propre, ainsi que la problématique de la
     mobilisation du financement nécessaire, et l’importance des coûts de
     traitement, transport et distribution des eaux usées, et du suivi de la qualité
     des eaux.
     Eu égard à ce qui précède, la Cour a recommandé au ministère de
     l’équipement et de l’eau de renforcer la gestion intégrée des ressources
     en eau en veillant à la préservation des réserves stratégiques en eaux
     souterraines et à l’encouragement du recours aux ressources non
     conventionnelles, notamment le dessalement des eaux de mer, la
     réutilisation des eaux usées traitées et la collecte des eaux pluviales, la
     réduction des pertes dans les réseaux de transport et de distribution de
     l’eau, ainsi qu’une meilleure protection des barrages contre l’envasement,
     en plus de l’accélération de réalisation des projets relatifs à
     l’interconnexion des bassins hydrauliques.
     La Cour a, également, recommandé au ministère de l’économie et des
     finances de mobiliser les financements nécessaires pour la mise en œuvre
     des programmes répondant aux défis posés.
     Elle a aussi recommandé au ministère chargé de l’Agriculture
     d’accélérer les programmes de reconversion à l’irrigation localisée.


        Rapport annuel de la Cour des comptes au titre de 2023-2024
32                    - Principaux axes -
La Cour a, enfin, recommandé aux ministères chargés de l’intérieur,
de l’équipement et de l’eau, de l’agriculture, et de la transition
énergétique de développer les synergies « Eau-Énergie-Agriculture »
permettant la convergence de ces trois secteurs.


                      Régionalisation avancée :
         Un chantier nécessitant le parachèvement du cadre
          juridique de la déconcentration administrative et
      l’accompagnement des Régions dans la mise en œuvre de
                          leurs compétences

La régionalisation avancée constitue un choix stratégique et consacre le
processus de décentralisation et de démocratie locale que le Maroc a adopté
de manière progressive depuis 1959. Dans la continuité de la mission
thématique que la Cour a menée sur la mise en œuvre de la régionalisation
avancée, elle a assuré, en 2024, le suivi de ce chantier, qui s’inscrit dans le
cadre de la vision éclairée de Sa Majesté le Roi et de ses Hautes Directives,
visant à « l'avènement de régions à part entière viables et stables dans le
temps, fondées sur des critères rationnels et réalistes, inhérents à un
système de régionalisation nouveau ». (Discours royal adressé à la nation
à l'occasion de l'installation de la Commission consultative de la
régionalisation, le 3 janvier 2010).
À cet égard, les pouvoirs publics ont poursuivi la mise en œuvre de projets
stratégiques pour accélérer l'instauration de la régionalisation avancée, à
travers un ensemble de réformes juridiques et institutionnelles relatives à
la décentralisation et à la déconcentration administrative. De plus, des
mécanismes renouvelés sont prévus et des ressources ont été alloués pour
accompagner les régions dans l’exercice de leurs compétences et pour
renforcer leurs capacités de gestion.
Concernant les ressources financières allouées par l’État aux régions,
la tendance haussière des contributions du fonds spécial relatif au produit
des parts d'impôts affectées aux régions s'est maintenue, passant de
3,79 MMDH en 2016 à 8,79 MMDH en 2023. Le montant total des
ressources transférées par l’État a atteint environ 52,76 MMDH pour la
période allant de janvier 2018 à fin juillet 2024, sans compter les ressources
du fonds de solidarité interrégionale, qui s’élèvent à 5,74 MMDH pendant
la même période.
En ce qui concerne le cadre juridique de la régionalisation avancée, un
nouveau décret a été promulgué en novembre 2023, fixant la procédure
d'élaboration, de suivi, de mise à jour et d'évaluation des programmes de


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              33
     développement régional (PDR) (décret n°2.22.475). Ce décret a abrogé
     celui du 29 juin 2016 (décret n° 2.16.299), visant, ainsi, à améliorer la
     méthodologie de préparation de ces programmes, à réguler les délais
     légaux de leur élaboration et à garantir la précision de leur contenu. À la
     lumière de ces nouvelles dispositions, le ministère de l’Intérieur a visé la
     deuxième génération des PDR pour la période 2022-2027, adoptés par les
     douze conseils régionaux.
     Néanmoins, l’atteinte des objectifs fixés par la régionalisation avancée,
     notamment l'accompagnement des régions dans l’exercice de leurs
     missions de développement, reste tributaire de la définition et de
     l’adaptation des textes législatifs et réglementaires régissant les domaines
     d’intervention des départements ministériels liés aux compétences des
     régions. Cela vise à délimiter les champs d’intervention des différents
     acteurs institutionnels et à atténuer le chevauchement de leurs attributions
     avec celles des régions.
     S’agissant de la mise en œuvre de la Charte nationale de la
     déconcentration administrative, pour compléter les mesures prévues par
     la feuille de route relative à son application, un décret portant délégation
     de pouvoirs et de signature (décret n°2.22.81) a été adopté le 30 mars 2023.
     De plus, un projet de décret relatif aux principes et règles d’organisation
     des administrations de l’État, ainsi qu’à la définition de leurs attributions a
     approuvé (projet de décret n° 2.22.80).
     Cependant, l’ancrage d’une culture de transfert des compétences
     décisionnelles du niveau central vers le niveau territorial nécessite des
     efforts supplémentaires, en accélérant, notamment, la mise en œuvre
     effective de la Charte nationale de la déconcentration administrative. À cet
     égard, il convient de noter que le taux de réalisation de la feuille de route
     de déconcentration administrative n’a atteint que 36% à la mi-octobre
     2024, contre 32% à la même période en 2023. De plus, le rythme de
     transfert et de délégation des compétences prioritaires en matière
     d’investissement vers les services déconcentrés reste insuffisant, , ne
     dépassant pas les 38% à la mi-octobre 2024, d’après les réponses du Chef
     du gouvernement.
     Concernant le cadre institutionnel, aucune représentation administrative
     commune ou sectorielle n’a été créée au niveau de l’administration
     régionale déconcentrée, malgré l’approbation par le Comité
     interministériel de déconcentration administrative de la création de cinq
     représentations régionales de l’État (deux directions régionales sectorielles
     et trois directions régionales communes) et du transfert de compétences
     décisionnelles vers celles-ci. Cette situation est due au retard dans
     l’adoption des projets de décrets fixant les attributions et l’organisation de


        Rapport annuel de la Cour des comptes au titre de 2023-2024
34                    - Principaux axes -
ces représentations ou dans l’aboutissement du consensus sur leurs
dispositions.
Par ailleurs, la loi organique relative aux régions a prévu la création
d’Agences Régionales d’Exécution des Projets (AREP) pour permettre aux
conseils régionaux de gérer leurs affaires. Depuis leur démarrage, ces
agences ont enregistré une augmentation constante du nombre de projets
qui leur sont confiés, avec des budgets d’investissement qui ont, ainsi,
atteint un total d’environ 10,77 MMDH en 2023, contre 8,24 MMDH en
2022 et 2,13 MMDH en 2018.
En matière de mécanismes de mise en œuvre de la régionalisation
avancée, la Cour a relevé un recours limité au mécanisme de
contractualisation entre l'État et les régions. Entre 2020 et 2022, quatre
régions seulement ont conclu des contrats État-Régions (CER), englobant
197 projets de développement pour un coût total de 23,56 MMDH.
Toutefois, le taux de projets achevés dans le cadre des quatre contrats n’a
pas dépassé 9 % à fin avril 2024, contre 7 % à fin 2022. En revanche, le
taux des projets en cours de réalisation a atteint 80 % à fin avril 2024.
En ce qui concerne les PDR couvrant la période 2022-2027, jusqu'à la mi-
octobre 2024, les Conseils régionaux n’avaient pas encore approuvé les
CER. Cette situation est liée à un manque de synchronisation entre la
planification de l'élaboration des contrats et celle des PDR. De plus, le
retard dans la nomination des chefs des représentations administratives
sectorielles et communes à l'échelle régionale, ainsi que dans la délégation
des compétences décisionnelles, n'a pas facilité le processus de
concertation sur le contenu des CER entre les régions et les ministères
concernés.
Pour ce qui est de la mise en œuvre des compétences partagées, et suite
aux recommandations de la Cour, le ministère de l'Intérieur a élaboré un
projet de décret visant à encadrer les modalités et conditions de conclusion
et de mise en œuvre des contrats entre l'État, les régions et d’autres
intervenants. Ce projet de décret, qui vise à généraliser le mécanisme de
contractualisation, définit la méthodologie de préparation, d'élaboration et
d'exécution des contrats, ainsi que les modalités de suivi, d'évaluation et de
coordination entre les différents acteurs. Ce projet est actuellement en
cours d'examen par le Secrétariat général du gouvernement avant d'être
soumis au Conseil du gouvernement pour approbation.
Le succès de la contractualisation entre l'État, les régions et les autres
parties prenantes demeure conditionné par l'adoption d'un cadre
réglementaire définissant clairement les obligations de chaque partie aux
différentes étapes de l'élaboration et l’exécution du contrat. Il est également
essentiel de rationaliser et maîtriser les délais des procédures relatives à la


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              35
     conclusion du contrat, afin de remédier aux insuffisances relevées dans la
     mise en œuvre de la première génération des PDR.
     Concernant les compétences transférées, l'élargissement progressif des
     attributions des régions nécessite l'adoption de principes de progressivité
     et de différenciation, ainsi qu'une mise en œuvre concrète des compétences
     propres. Il est également crucial d’évaluer la capacité des régions à exercer
     les compétences qui leur sont transférées, notamment en termes de
     ressources, afin d’éviter de les surcharger de compétences multiples. Dans
     ce cadre, il y a lieu de préciser que les mécanismes encadrant l'application
     du principe de différenciation dans le transfert des compétences restent
     encore à établir, notamment à travers la définition de critères d'évaluation
     de la capacité des régions à exercer les compétences qui leur seront
     confiées, tout en tenant compte des spécificités propres à chacune.
     Eu égard à ce qui précède, la Cour a recommandé au Chef du
     gouvernement d’accélérer la mise en œuvre des actions programmées
     dans la feuille de route pour l'exécution de la Charte nationale de la
     déconcentration administrative, d’en évaluer les résultats et d'assurer les
     conditions et les moyens nécessaires pour garantir la périodicité des
     travaux de la Commission interministérielle de la déconcentration
     administrative.
     Elle a également recommandé d’accélérer l’adoption des cinq décrets
     définissant les attributions et l’organisation des représentations
     administratives communes et sectorielles au niveau régional, approuvés
     par la Commission interministérielle de la déconcentration administrative,
     et ce afin d'assurer l'unité de l’action des services déconcentrés de l'État et
     de garantir une meilleure coordination entre eux.
     De plus, la Cour a recommandé au ministère de l’Intérieur d’établir un
     plan d’action, assorti d’un calendrier, pour adapter les textes législatifs et
     réglementaires relatifs aux compétences des départements ministériels en
     fonction des compétences propres et partagées des régions, et ce en
     coordination avec les ministères concernés.
     La Cour a recommandé, également, d'accompagner et de soutenir les
     régions dans la mise en œuvre des PDR approuvés, afin de pallier les
     insuffisances précédentes, tout en tenant compte de leurs capacités de
     gestion et des ressources financières disponibles. Elle a, enfin,
     recommandé de veiller à une identification précise des projets prioritaires
     à réaliser dans le cadre des contrats État-Région, en intégrant des
     mécanismes appropriés pour garantir leur succès, notamment en précisant
     les formalités et conditions de conclusion et d’exécution de ces contrats.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
36                    - Principaux axes -
                Réforme de la Protection sociale :
      Défis d’une généralisation effective et d’un financement
         durable pour atteindre les objectifs de la réforme

La généralisation de la protection sociale fait partie des grands chantiers
lancés par Sa Majesté le Roi que Dieu l’assiste. Son implémentation qui
enregistre des avancées notables est aussi confrontée à certains défis liés
essentiellement à la généralisation, au financement durable et à la réforme
du secteur hospitalier public.
Les autorités publiques se sont focalisées sur l’instauration des outils
d’implémentation et le renforcement de l’arsenal juridique régissant le
système de la protection sociale, de manière générale, et sur la
généralisation de l’assurance maladie obligatoire de base (AMO) et de
l’aide sociale directe (ASD) en particulier. L’élargissement de la base des
adhérents aux régimes de retraite et la généralisation de l’indemnité
pour perte d’emploi sont actuellement en phase d’encadrement juridique.
Concernant la généralisation de l’AMO, après la promulgation des
textes législatifs et réglementaires, l’instauration des procédures et la
mobilisation des ressources nécessaires pour sa mise en œuvre, le nombre
d’assurés principaux au titre du régime de l’AMO pour les catégories des
professionnels, des travailleurs indépendants et des personnes non salariées
exerçant une activité libérale a atteint 1,68 millions d’assurés principaux
au 10 septembre 2024, soit 56% de la population cible de ce régime.
Toutefois, le nombre des assurés principaux ayant des droits ouverts ne
dépasse pas 1,2 millions, et le taux de recouvrement des contributions dues
est seulement de l’ordre de 37%, ce qui est de nature à impacter l’équilibre
financier du régime.
S’agissant du régime de l’AMO des personnes qui ne peuvent pas
s’acquitter de leurs cotisations (AMO TADAMON), le nombre des assurés
principaux a dépassé 4,05 millions et le montant des transferts de l’Etat à
la Caisse nationale de sécurité sociale (CNSS), au titre de ce régime, s’est
établi à 15,51 MMDH pour la période allant de décembre 2022 à fin
septembre 2024. A noter qu’environ 74% des dépenses des prestations de
soins de ce régime se sont orientés vers le secteur privé.
Quant à l’AMO des personnes ayant la capacité de cotiser et n'exerçant
aucune activité salariale ou non salariale (AMO CHAMIL), environ
133.000 personnes y sont inscrites, dont 67% disposent des droits ouverts.




                                         Rapport annuel de la cour des comptes au titre de 2023-2024
                                                      - Principaux axes -                              37
     Concernant l’ASD, sa mise en œuvre a démarré en décembre 2023, après
     la promulgation des textes juridiques et réglementaires le régissant, la
     conclusion des conventions relatives à son implémentation et la
     mobilisation des ressources nécessaires pour son financement. Jusqu’au
     mois de septembre 2024, un nombre cumulé de 4,18 millions de familles a
     bénéficié du programme. Au titre du mois de septembre 2024, 3,9 millions
     de foyers en ont bénéficié, dont 2,36 millions de bénéficiaires d’allocations
     relatives à l’enfance et 1,55 millions de bénéficiaires d’allocations
     forfaitaires.
     De plus, le nombre de bénéficiaires de l’aide à la rentrée scolaire s’élève à
     1,78 millions de familles. Ainsi, ont bénéficié de cette aide 1,66 millions
     élèves du cycle primaire, 959 mille élèves du cycle collégial et 438 mille
     élèves lycéens.
     Le coût global de l’aide sociale directe, depuis sa mise en œuvre jusqu’au
     10 octobre 2024, s’élève à 18,54 MMDH. Sachant que l’aide dédiée aux
     orphelins et aux enfants délaissés domiciliés aux établissements de
     protection sociale est actuellement en cours de mise en œuvre.
     En dépit des avancées notables enregistrées, la réforme de la protection
     sociale connait certains défis. Ils sont particulièrement liés au
     développement du système de ciblage, à la maitrise des effectifs des
     catégories prises en charge par l’Etat, à la diversification des sources de
     financement en vue d’alléger la pression sur le budget de l’Etat, au
     développement et à la mise à niveau des établissements de soins publics et
     à la lutte contre la vulnérabilité à travers la substitution de l’aide par le
     revenu.
     Compte tenu de ces défis, la Cour a recommandé principalement, au
     Chef du Gouvernement, d’activer l’ensemble des instances intervenant
     dans la gestion du système de protection sociale, la mobilisation et la
     diversification de sources de financement durables, le développement et la
     mise à niveau des établissements de soins publics, le suivi de l’impact de
     l’aide sociale directe sur les catégories sociales bénéficiaires et la
     coordination entre la politique de la protection sociale et les autres
     politiques économiques et sociales.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
38                    - Principaux axes -
                   Réforme de l’investissement :
     Cadre stratégique et de pilotage en cours d’achèvement et
     nécessité de poursuivre la mise en place des dispositifs de
                              soutien

La réforme de l’investissement revêt une importance cruciale dans le
renforcement de la position du Maroc en tant que pôle d’attractivité
régionale pour l’investissement, et dans la consolidation de son
positionnement en tant que destination stable pour un investissement
productif, compétitif et respectant l’environnement. Le déploiement de
cette réforme permettrait la dynamisation de l’économie nationale, la
création d’emplois stables, la réduction des disparités spatiales et le
développement du pays dans son ensemble.
L’intérêt particulier accordé à cette réforme se traduit dans les différentes
orientations stratégiques du pays, notamment dans les discours de Sa
Majesté le Roi qui a, à différentes reprises, souligné son importance
cruciale pour le pays, notamment à l’occasion du discours d’ouverture du
Parlement en octobre 2022, dans lequel Sa Majesté le Roi avait érigé
l’investissement, au même titre que la problématique de l’eau, en tant que
sujets prioritaires pour le pays. Il avait alors insisté sur « la nécessité
d’opérer un bond qualitatif en matière de promotion de l’investissement ».
Le souverain avait également appelé à l’adoption d’un « pacte national
pour l’investissement », à la mise en œuvre effective de la charte de
déconcentration administrative, au renforcement du rôle des centres
régionaux de l’investissement et à l’amélioration de l’environnement
global des affaires. Sa Majesté a également ordonné, dans Son discours en
date du 6 novembre 2024 à l’occasion du 49ème anniversaire de la marche
verte, d’ouvrir de nouvelles perspectives aux marocains résidant à
l’étranger qui sont désireux d’investir dans leur pays.
Concernant le cadre stratégique relatif au développement de
l’investissement privé, il s’est considérablement amélioré au cours des
dernières années. Il a, en effet, été consolidé par la vision stratégique,
tracée par le nouveau modèle de développement, et par la fixation du
premier objectif stratégique de déclinaison de cette vision, consistant en la
réalisation de 550 MMDH d’investissements et la création de 500.000
emplois. Un premier cap stratégique que le ministère en charge de
l’investissement a décliné, en coordination avec les centres régionaux de
l’investissement, aux niveaux sectoriel et territorial, à travers, notamment,
des actions d’information et de mobilisation des différents acteurs
concernés.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              39
     Cette avancée tangible dans le cadre stratégique de l’investissement
     gagnerait, cependant, en qualité par l’adoption de la stratégie nationale de
     l’investissement, prévue le décret portant attributions du ministère délégué
     à l’investissement. Cette stratégie apporterait, notamment, plus de
     cohérence aux choix économiques et sectoriels, et plus de clarté et de
     convergence aux contributions des différents autres acteurs, notamment
     celles des fonds souverains dédiés à l’investissement et au développement,
     tels que le fonds Mohammed VI pour l’investissement, le fonds Hassan II
     pour le développement économique et social et le fonds Ithmar Capital. De
     même, il convient d'attirer l'attention sur l'importance de l’adoption du
     pacte pour l’investissement, qui permettrait d’améliorer ce cadre
     stratégique en officialisant les engagements des différentes parties
     prenantes.
     S’agissant du système de soutien à l’investissement, et bien que les
     textes réglementaires se rapportant au dispositif principal et au dispositif
     spécifique relatif aux projets stratégiques aient été adoptés dans les délais
     prévus, ceux concernant les dispositifs spécifiques aux très petites, petites
     et moyennes entreprises (TPE et PME) et ceux relatifs investissements des
     marocains à l’étranger ne sont pas adoptés à date d’octobre 2024. Le
     dispositif se rapportant aux TPE et PME, en particulier, revêt un intérêt
     crucial pour l’encouragement à l’investissement initié par cette
     composante principale qui représente 93% du tissu économique et
     productif du Royaume, selon les données du Haut-commissariat au Plan.
     Un dispositif qui reste cependant assez complexe à déployer, notamment
     en raison de l’équilibre à trouver entre sa valeur ajoutée pour l’économie
     et son coût, d’une part, et la nécessité d’un déploiement équilibré et inclusif
     de la réforme de l’investissement.
     Pour ce qui est de l’amélioration du climat des affaires, les réalisations
     se rapportant au déploiement de la feuille de route stratégique sont
     globalement satisfaisantes, puisque 74% des initiatives qui y sont prévues
     ont déjà été lancées et que certains chantiers structurels pour l’amélioration
     de l’environnement global des affaires ont connu des avancées
     significatives, notamment en matière de simplification des procédures, où
     22 actes traités au niveau des centres régionaux d’investissement et des
     commissions régionales unifiées d’investissement ont vu les documents
     demandées aux investisseurs réduits de 45%, au moment où 15 parcours
     prioritaires de l’investisseur sont en cours d’optimisation. Le taux global
     annoncé dans le déploiement de la feuille de route stratégique est de l’ordre
     de 31% des initiatives déjà lancées. Ce rythme de déploiement devrait être
     maintenu, voire accéléré à deux années du terme prévu pour la réalisation
     de l’ensemble des objectifs.



        Rapport annuel de la Cour des comptes au titre de 2023-2024
40                    - Principaux axes -
Il convient de noter, également, que la mobilisation du foncier occupe une
place importante dans la concrétisation du deuxième pilier de la feuille de
route stratégique et dans l’amélioration d’ensemble du climat des affaires,
nécessitant, ainsi, davantage de coordination et d’adhésion de la part des
différents acteurs. Deux préalables requièrent, à ce titre, une attention
particulière en raison de leur impact potentiel sur l’acte d’investir, en
l’occurrence, l’adoption d’une stratégie foncière déterminant avec
précision les besoins en la matière, afin de reconstituer la réserve foncière,
et l’amélioration des liens et de la complémentarité entre les différents
statuts du foncier (domaine privé, terres collectives, terres Guich, domaine
forestier, …).
Eu égard à ce qui précède, la Cour des comptes a recommandé au Chef
du gouvernement d’améliorer le cadre stratégique de la réforme en
accélérant l’adoption d’une stratégie nationale de l’investissement et en
formalisant le pacte national de l’investissement, afin d’officialiser les
engagements respectifs des secteurs privé et bancaire ; et d’accélérer la
mise en place de l’observatoire national de l’investissement pour mieux
piloter et suivre les réalisations des objectifs stratégiques, notamment aux
niveaux territorial et sectoriel.
Elle a également recommandé de compléter les dispositifs de soutien à
l’investissement par l’adoption des textes réglementaires se rapportant au
dispositif spécifique aux TPE et PME, afin de garantir un déploiement
cohérent et inclusif de la réforme, et de maintenir le rythme de déploiement
de la feuille de route stratégique relative à l’amélioration du climat des
affaires, notamment en ce qui se rapporte à la mobilisation du foncier
destiné à l’investissement, en renforçant l’implication de tous les acteurs
concernés.


      Le secteur des établissements et entreprises
                        publics :
    Politique actionnariale de l’Etat, une mise en œuvre à
                          accélérer

La réforme du secteur des établissements et entreprises publics (EEP) vise
à restructurer leur portefeuille et renforcer la fonction de l’Etat-actionnaire
afin d’améliorer l’efficacité socio-économique des EEP stratégiques. Par
ailleurs, la création du fonds Mohammed VI pour l’investissement vise à
accompagner le plan de relance de l’économie nationale et à faire du
capital-investissement un levier pour contribuer à la réalisation de



                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              41
     l’objectif national de mobilisation de 550 MMDH d'investissement et de
     création de 500.000 emplois à l’horizon 2026.
     Compte tenu du rôle central des EEP dans le portage des chantiers
     structurants, la Cour a accordé une attention particulière aux actions
     critiques qui conditionnent le rythme d’avancement de la réforme dans sa
     globalité.
     En ce qui concerne la restructuration du portefeuille public, des
     progrès importants ont été accomplis dans la clarification de sa vision.
     Néanmoins, une plus grande mobilisation des départements ministériels de
     tutelle s’avère nécessaire pour sa finalisation. Ainsi, les efforts déployés
     par le ministère de l’économie et des finances ont permis une amélioration
     de la vision sur le portefeuille cible des établissements publics à caractère
     administratif en termes de taille et de composition, sans pour autant
     permettre d’arrêter une feuille de route exhaustive des opérations de
     restructuration avec un échéancier précis. A ce titre, la Cour attire
     l’attention sur l’importance de la mobilisation et de la participation des
     départements ministériels de tutelle afin d’aboutir à des plans de
     restructuration réalistes et applicables eu égard à la complexité de la
     détermination des scénarios de restructuration.
     Par ailleurs, en dépit de l’ambition, affichée depuis 2018, de relancer le
     programme des privatisations, afin de l’inscrire, à moyen et long terme
     dans le cadre des opérations de redimensionnement du portefeuille public
     pour servir l’objectif de réduction de sa taille, tel qu’énoncé par la loi cadre,
     le nombre d’opérations de privatisation réalisé entre 2018 et 2024 reste
     limité. En effet, seulement quatre opérations ont été réalisées pour un
     produit de cession qui n’a pas dépassé 17 MMDH.
     Concernant la feuille de route de la politique actionnariale de l’Etat,
     l’approbation des orientations stratégiques relatives à cette politique en
     Conseil des ministres, le 1er juin 2024, marque une étape importante dans
     l’opérationnalisation du rôle de l'Agence nationale de gestion stratégique
     des participations de l'Etat (ANGSPE)dans sa fonction de portage de la
     fonction actionnariale de l’Etat. En outre, le projet de la politique
     actionnariale de l’Etat, qui traduit les orientations stratégiques, précitées,
     et la feuille de route de sa mise en œuvre ont été examinés par le comité de
     stratégie et d’investissement de l’ANGSPE en date du 27 juin 2024 et
     approuvés par son Conseil d’Administration en date 3 juillet 2024. Ce
     projet a obtenu l’avis favorable de l’instance de Concertation sur la
     Politique Actionnariale de l’Etat le 19 septembre 2024. Néanmoins, la
     Cour attire, à ce sujet, l’attention sur le besoin d’accélérer la mise en œuvre
     de ladite feuille de route.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
42                    - Principaux axes -
Par ailleurs, en dépit des efforts déployés par l’ANGSPE, le processus de
transformation des quinze établissements publics relevant de son périmètre
en sociétés anonymes, tel que prévu par l’article 28 de la loi n°82-20
portant création de l’agence, n’avance toujours pas au rythme nécessaire
pour respecter le délai légal de cinq années. A ce titre, la Cour souligne la
nécessité de la mobilisation des départements ministériels de tutelle, qui
sont les véritables porteurs des projets de lois de transformation des
établissements publics précités, en vue de respecter le délai précité.
Quant à l’opérationnalisation du fonds Mohammed VI, dans son volet
relatif à la création des fonds sectoriels et thématiques prévus par l’article
4 de la n°76-20 portant sa création, le premier appel à manifestation
d’intérêt lancé par le fonds, le 8 mai 2023, pour la sélection de sociétés de
gestion appelées à créer et à gérer les fonds précités, a abouti à la sélection
de 15 sociétés de gestion avec lesquelles les règlements de gestion sont en
cours de négociation, pour un volume global de capital investissement de
18,5 MMDH, dont 4,7MMDH à débourser par le Fonds Mohammed VI et
13,8 MMDH mobilisés par les sociétés de gestion auprès d’investisseurs
locaux et internationaux.
En revanche, le financement des projets d’infrastructures des EEP sous
forme de partenariat public-privé, pour soulager le budget de l’Etat avec
l’appui d’investisseurs internationaux, est toujours dans la phase
d’identification des projets stratégiques et des projets d’infrastructures
dans lesquels le Fonds Mohammed VI envisage apporter une partie du
financement en contrepartie de participations minoritaires (intervention en
fonds propres). En effet, quelques projets ont été identifiés pour lesquelles
les discussions sont en cours pour achever la structuration financière.
Eu égard à ce qui précède, la Cour a réitéré, en vue d’accélérer leur mise
en œuvre, les recommandations émises dans son rapport annuel de 2022-
2023, portant sur le parachèvement de la composition des conseils
d’administration de l’ANGSPE et du Fonds Mohammed VI pour
l’investissement, conformément aux dispositions légales, afin de leur
permettre de remplir leurs fonctions d’orientation stratégique et de
contrôle ; et sur le démarrage du transfert au profit de l’ANGSPE de la
propriété des participations que l’Etat détient dans les EEP à caractère
marchand et accélérer la mise en œuvre de la restructuration du portefeuille
de ces EEP.
En outre, elle a recommandé au ministère de l’économie et des
finances, aux ministères de tutelle des EEP, à l’ANGSPE et au Fonds
Mohammed VI pour l’investissement, d’accélérer le déploiement de la
feuille de route de la politique actionnariale de l’Etat après son adoption
par le conseil du gouvernement ; et d’activer la mise en œuvre des


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              43
     opérations de restructuration des EEP non marchands, avec l’initiative des
     ministères de tutelle, à qui incombe la mission de proposer les plans
     d’organisation institutionnelle de leurs secteurs, sur la base d’une nouvelle
     vision et d’une stratégie actualisée ;
     Elle a recommandé, également, d’achever les opérations de liquidation
     des EEP en priorisant celles qui comportent des enjeux d’actifs et de passifs
     pour l’Etat ; et de parachever la préparation et la publication des textes
     législatifs et réglementaires prévus par la réforme.
     La Cour a recommandé, enfin, d’activer la transformation des
     établissements publics relevant de l’ANGSPE en sociétés anonymes, en
     concertation avec les ministères de tutelle à qui incombe la préparation des
     textes juridiques; et d’achever les travaux d’identification et de
     structuration financière du portefeuille des projets d’infrastructures des
     EEP, qui seront appuyés par le Fonds Mohammed VI pour
     l’investissement, en priorisant les secteurs stratégiques.


                                                     Réforme fiscale :
         Une mise en œuvre continue des dispositions de la loi-cadre
          nécessitant l’accélération de la mise en place des autres
                            mesures prioritaires

     Loi-cadre cadre n° 69.19 du 26 juillet 2021 a précisé les orientations, les
     objectifs, les mécanismes et les modalités de mise en œuvre progressive
     des mesures prioritaires de la réforme fiscale, et a fixé un délai de cinq ans
     à compter du mois d’août 2021 pour leur mise en œuvre. Cette réforme,
     vise principalement, à asseoir un système fiscal efficace, juste, équitable et
     équilibré permettant de mobiliser le plein potentiel fiscal pour le
     financement des politiques publiques.
     Durant la première moitié du délai de la mise en œuvre de la loi-cadre
     précitée, les principales mesures apportées, par les lois de finances (LF) de
     2023 et de 2024, ont concerné respectivement, de manière principale,
     l’impôt sur les sociétés (IS) et la taxe sur la valeur ajoutée (TVA).
     S’agissant de l’IS, la principale mesure introduite a porté sur la révision
     des taux en vue d'atteindre progressivement, à l’horizon de 2026, les taux
     cibles de 20% applicables aux sociétés dont le bénéfice net est inférieur à
     100 MDH, de 35% pour celles ayant un bénéfice net égal ou supérieur à
     100 MDH, et 40 % pour les établissements de crédit et organismes
     assimilés et les entreprises d'assurances. La cotisation minimale a été revue
     également à la baisse passant de 0,5% à 0,25% du chiffre d’affaires.


        Rapport annuel de la Cour des comptes au titre de 2023-2024
44                    - Principaux axes -
En ce qui concerne la TVA, la principale mesure apportée par la LF 2024
a consisté en la réduction du nombre des taux de la TVA (7%, 10%, 14%
et 20 %) et l’alignement progressif vers deux taux cibles (10% et 20%) à
l’horizon de 2026. De même, l’exonération de la TVA a été généralisée
aux produits de base de large consommation, tels que les produis
pharmaceutiques, les fournitures scolaires et les matières entrant dans leur
fabrication. Cette exonération a concerné également la vente et la livraison
de l’eau destinée à un usage domestique et les prestations d’assainissement.
De plus, il a été institué le régime de l’auto-liquidation de la TVA et d’un
nouveau régime de retenue à la source de cette taxe.
Concernant les mesures de réforme prévues dans le PLF 2025, elles
portent essentiellement sur l’impôt sur le revenu (IR). Ainsi, il est prévu le
réaménagement du barème progressif de l’IR à compter du 1er janvier 2025,
et ce par le relèvement de la première tranche du barème relative au revenu
net exonéré de 30.000 DH à 40.000 DH, l’élargissement des autres tranches
et la réduction du taux marginal de 38% à 37%. Le PLF précité prévoit
également l’augmentation du montant annuel de la réduction de l’impôt sur
le revenu au titre des charges familiales, en relevant le montant de la
déduction de 360 à 500 DH par personne à charge et le relèvement du
plafond de cette réduction de 2.160 DH à 3.000 DH.
De même, il est prévu de relever le seuil d’application de la retenue à la
source sur les revenus fonciers de 30.000 à 40.000 DH. Par ailleurs, il est
proposé de permettre l’option d’imposition des revenus bruts fonciers des
particuliers d’un montant égal ou supérieur à 120.000 DH, par l’application
d’un taux libératoire de 20% avec possibilité de bénéficier de la dispense
de la déclaration annuelle du revenu global pour ces revenus.
En outre, dans le cadre de la lutte contre l’évasion fiscale, il est prévu de
soumettre à l’impôt sur le revenu tous les autres revenus et gains, non
intégrés dans les cinq catégories de revenus prévus par l’article 22 du code
général des impôts.
De même, afin d’améliorer la lisibilité des textes fiscaux et d’assurer
l’équité fiscale, le PLF de 2025 a prévu la clarification du principe
d’imposition des profits fonciers réalisés suite à l’expropriation par voie de
fait ou suite à tout autre transfert de propriété par une décision judiciaire
ayant force de la chose jugée. Il est proposé également d’instituer
l’obligation d’opérer une retenue à la source sur les indemnités versées par
les personnes intervenant dans le paiement de ces indemnités.
Outre les mesures relatives à l’IR, d’autres dispositions du PLF concernent
la TVA, il s’agit notamment de l’augmentation de 30% à 32% de la part
minimale du produit de cette taxe affectée aux collectivités territoriales.
Les autres mesures sont relatives aux droits d’enregistrement telles que


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              45
     l’institution de l’obligation pour les notaires de transmettre à
     l’administration fiscale, par voie électronique les actes portant une
     signature électronique, l’institution d’une amende applicable aux
     professionnels chargés d’accomplir les formalités de l’enregistrement par
     voie électronique, en cas de non renseignement des informations
     obligatoires, de communication d’informations erronées ou de non
     transmission de l’acte enregistré par voie électronique.
     Toutefois, à l’approche du terme du délai fixé par la loi cadre relative
     à la réforme fiscale, d’autres mesures prioritaires ne sont pas encore mises
     en œuvre, particulièrement la révision des bases relatives à la fiscalité
     territoriale, et ce après les amendements apportés par la loi 07.20 modifiant
     et complétant la loi 47.06 relative à la fiscalité des collectivités locales.
     De plus, exceptée l’intégration de certaines taxes parafiscales dans le code
     général des impôts, tel que proposé par le PLF de 2025 pour la taxe spéciale
     sur le ciment, les mesures visant à rationaliser et à simplifier les règles
     d’assiette et de recouvrement de la parafiscalité comme prescrit par la loi-
     cadre n’ont pas encore été édictées.
     Au vu de ce qui précède, tout en notant la poursuite de la mise en œuvre
     de la loi-cadre n°69.19 portant réforme fiscale, la Cour réitère ses
     recommandations émises dans son rapport annuel 2022-2023, adressées
     au Chef du Gouvernement et portant sur l’activation de la mise en œuvre
     de la réforme de la fiscalité des collectivités territoriales et de la
     parafiscalité conformément aux objectifs fixés par la loi-cadre, et sur
     l’évaluation régulière de l’impact socio-économique des avantages fiscaux
     octroyés afin d’orienter les décisions quant à leur maintien, leur révision
     ou leur suppression selon le cas.
     Enfin, la Cour a recommandé au ministère de l’économie et des
     finances de réaliser une évaluation de l’impact des mesures mises en
     œuvre dans le cadre de la réforme relative à la TVA et à l’IS et de
     communiquer au sujet de cette évaluation et des effets attendus de la
     réforme proposée en matière de l’IR, tant au niveau budgétaire qu’au
     regard des objectifs fixés par la loi cadre susvisée.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
46                    - Principaux axes -
   Evaluation des programmes et projets
                  publics

         Stratégie énergétique nationale 2009-2030 :
      l’atteinte des objectifs de la transition énergétique reste
          tributaire de la révision des composantes et de la
     gouvernance de la stratégie et l’accélération de la réforme
                      du secteur de l’électricité

La Stratégie énergétique nationale 2009-2030 (SEN) a fixé comme
objectifs stratégiques la sécurité d’approvisionnement et la disponibilité de
l’énergie, la généralisation de l’accès à l’énergie à des prix compétitifs, la
maîtrise de la demande énergétique et la préservation de l’environnement.
Dans cette optique, ses orientations stratégiques se sont articulées,
principalement, autour de l’obtention d’un mix énergétique optimisé
reposant sur des choix technologiques fiables et compétitifs, la
mobilisation des ressources nationales par la montée en puissance des
énergies renouvelables (EnR) et le développement de l’efficacité
énergétique, érigée en priorité nationale, ainsi que le renforcement de
l’intégration régionale.
Dans ce cadre, pour pallier l'urgence induite par l’insuffisance des
capacités électriques durant les années 2000, la SEN a intégré à moyen
terme le Plan national d'actions prioritaires (PNAP) 2009-2013. Ce plan
visait à rétablir l'équilibre entre l'offre et la demande d'électricité en
renforçant l'offre via la construction de nouvelles centrales électriques et
en améliorant les dispositifs d’efficacité énergétique.
Outre le PNAP, la Stratégie énergétique nationale englobe un ensemble de
composantes comprenant les secteurs de l’électricité, des énergies
renouvelables, de l’efficacité énergétique, des combustibles et carburants,
de l’électronucléaire, de l’exploration pétrolière, des schistes bitumineux
et des bioénergies. Des avancées significatives dans plusieurs domaines
ont été accomplies et ont permis de consolider le positionnement du Maroc
en tant que pays engagé dans la transition énergétique. En revanche, des
aspects méritent encore une amélioration, notamment la gouvernance du
secteur énergétique et le niveau d’atteinte des objectifs fixés pour chacune
des composantes de la stratégie.
S’agissant de la gouvernance du secteur, le processus de planification
s’est limité principalement au secteur de l’électricité avec, notamment,


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              47
     l’élaboration de plans d'équipement associés à la production et au transport
     de l'énergie électrique, alors que d'autres aspects importants, tels que la
     sécurité d’approvisionnement, l'efficacité énergétique et la diversification
     des sources d'énergie, n’ont pas été approchés. Ceci met en évidence la
     nécessité d’instaurer une vision holistique dans la planification
     énergétique.
     Par ailleurs, les réunions des instances de gouvernance des établissements
     et entreprises publics (EEP) opérant dans le secteur de l'énergie ont été
     caractérisées par leur irrégularité. A titre d’exemple, le conseil
     d'administration de l’Office national de l’électricité et de l’eau potable
     (ONEE) n'a tenu que cinq réunions au cours de la période 2010-2023, sur
     28 réunions qui devaient se tenir conformément à la loi.
     La Cour a constaté, également, un recours limité à la contractualisation
     entre l’Etat et ces EEP, malgré le lancement d’un ensemble d’initiatives
     dans ce sens. Ainsi, depuis l’année 2008, soit à la veille du lancement de
     la SEN, seul l’ONEE a conclu deux contrats programme avec l’Etat : un
     premier couvrant la période 2008-2011, puis un deuxième pour la période
     2014-2017.
     En outre, il convient de souligner que le secteur de l’électricité a connu,
     depuis le lancement de la SEN, une ouverture progressive sur le secteur
     privé pour la production et la commercialisation de l’électricité suite, à
     l’adoption de la loi n°13.09 relative aux énergies renouvelables. De même,
     la régulation du secteur de l’électricité a été renforcée, en 2016, avec
     l’adoption de la loi n°48.15 relative à la régulation du secteur et à la
     création de l’Autorité nationale de régulation de l’électricité. Cependant,
     d'autres secteurs, tels que le gaz et les produits pétroliers, nécessitent
     également la mise en place d’instances de régulation pour les accompagner
     vers l’atteinte d’un niveau élevé de compétitivité.
     En ce qui concerne les réalisations enregistrées dans les différentes
     composantes de la SEN, la part des énergies renouvelables dans le mix
     électrique, en termes de capacités de production installées, est passée de
     32% en 2009 à 40% à fin 2023, restant ainsi en deçà de l’objectif de 42%
     fixé pour l’année 2020. Cela s'explique par le retard dans la réalisation d'un
     certain nombre de projets de production de ces énergies. De plus, plusieurs
     projets présentés par le secteur privé conformément à la loi n°13.09,
     précitée, n’ont pas été autorisés faute de capacités suffisantes du réseau de
     transport de l'électricité.
     En outre, le transfert des installations et des projets d’énergies
     renouvelables de l’ONEE à MASEN a connu un retard significatif. En
     effet, à fin septembre 2024, cette opération n’a pas encore eu lieu, alors
     que la loi n°38.16 modifiant et complétant le Dahir portant création de


        Rapport annuel de la Cour des comptes au titre de 2023-2024
48                    - Principaux axes -
l’ONEE a fixé la fin du mois de septembre 2021 comme date limite pour
cette opération.
La séparation des rôles dans le secteur de l'électricité a également été
retardée. En effet, et jusqu’à la fin de l'année 2023, la séparation comptable
des activités de production, de transport et de distribution de l’ONEE n'a
pas été réalisée. De plus, aucune date limite n'a été fixée pour clôturer cette
opération. Ceci est de nature à retarder l’atteinte d’un des objectifs
importants de la loi n°48-15, à savoir l’instauration d’un gestionnaire du
réseau
Pour ce qui est de l’électronucléaire et la biomasse, considérés par la SEN
comme options ouvertes pour renforcer la sécurité énergétique, la Cour a
relevé qu’à fin 2023, le développement desdites options demeure toujours
dans une phase embryonnaire.
Par ailleurs, la SEN a adopté l’efficacité énergétique comme priorité
nationale. Dans ce cadre, une première version de la stratégie nationale
d’efficacité énergétique a été élaborée en 2014, suivie d’une deuxième
version en 2019. Toutefois, aucune des deux versions n’a été approuvée.
Ceci a entravé la mise en œuvre des mesures prévues. De plus, la faiblesse
des moyens financiers, le retard de publication de certains textes
d’application de la loi 47.09 relative à l’efficacité énergétique et l'absence
d'un dispositif d’incitation capable de faire adhérer les secteurs énergivores
ont également contribué à la mise en œuvre limitée des mesures
d’efficacité énergétique.
Concernant le secteur des hydrocarbures, depuis l’adoption de la SEN, les
stocks de réserve des divers produits pétroliers sont restés en deçà du
niveau requis de 60 jours. A titre d’exemple, en 2023, les stocks de gaz,
d'essence et de gaz butane n'ont pas dépassé respectivement 32, 37 et 31
jours. Un progrès limité a été enregistré également au niveau de la
diversification des points d'entrée des produits pétroliers importés. En
effet, un seul nouveau point d’entrée a été réalisé, depuis le lancement de
la stratégie en 2009, et ce au niveau du port de Tanger Med.
S’agissant du secteur du gaz naturel, le non aboutissement des initiatives
prises pour développer ce secteur affecte les efforts visant à abandonner
progressivement le charbon dans la production de l'électricité. A ce titre,
plusieurs initiatives ont été lancées depuis 2011, mais n'ont pas abouti à
l’adoption d'une stratégie officielle pour le développement de ce secteur.
Eu égard à ce qui précède, la Cour a recommandé au Chef du
gouvernement de veiller à l’élaboration, la validation et la mise en œuvre
d’une stratégie nationale d’efficacité énergétique, et à la mise en place d’un




                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              49
     système incitatif à même d’encourager les mesures d’efficacité
     énergétique.
     La Cour a également recommandé au ministère de la transition
     énergétique et du développement durable, d’instaurer un cadre de
     gestion basé sur des contrats programmes entre l’Etat et les établissements
     et entreprises publics du secteur énergétique, tout en veillant à l’application
     de leurs clauses.
     Concernant le secteur de l’électricité, la Cour a recommandé d’en
     accélérer la réforme, à travers la séparation des rôles dans ce secteur, la
     publication des textes juridiques restants, relatifs à sa régulation,
     notamment ceux liés à la création et au fonctionnement du gestionnaire du
     réseau de transport. Elle a également recommandé l’achèvement de
     l’opération de transfert des installations des énergies renouvelables de
     l’ONEE à MASEN.
     De plus, la Cour a recommandé au ministère de mettre en place de
     mécanismes de gestion et de contrôle des stocks de sécurité, permettant de
     pallier les effets des fluctuations des prix du marché à l’international et
     leurs répercussions sur les prix au niveau national. Elle a, enfin,
     recommandé au ministère la mise en place d’une stratégie gazière
     concertée et d’un cadre juridique adéquat, permettant l’émergence d’un
     marché gazier transparent et attractif aux investissements.


                              Stratégie nationale de lutte contre
                                      l’analphabétisme :
        Modeste impact des programmes et nécessité d’amélioration
                         mécanismes de ciblage

     Le processus de lutte contre l'analphabétisme a connu une série de réformes
     structurelles, incluant la création de l'Agence nationale de lutte contre
     l'analphabétisme (l’agence) et l’allocation d’un soutien financier,
     pédagogique et technique aux acteurs de la société civile pour la mise en
     œuvre des programmes de lutte contre l'analphabétisme. À cet effet, une
     enveloppe globale de près de 2.971 MDH a été mobilisée au profit de
     l'agence, depuis le lancement de ses programmes en 2015 jusqu'à la fin de
     l'année 2023.
     Néanmoins, la mise en œuvre des plans stratégiques et des programmes de
     lutte contre l'analphabétisme, par les différents acteurs, n'a pas encore
     produit l'effet escompté pour éradiquer ce fléau. En effet, malgré les efforts
     déployés, la proportion d'analphabètes demeure élevée chez les citoyens


        Rapport annuel de la Cour des comptes au titre de 2023-2024
50                    - Principaux axes -
âgés de plus de 15 ans, avec plus de 9 millions et 240 mille personnes
enregistrées en 2021, soit l’équivalent d’un taux d'analphabétisme
d'environ 34,2% contre 47,7% en 2004.
Concernant le cadre stratégique, la lutte contre l'analphabétisme a
connu, depuis 2004, une succession de stratégies nationales et de plans
d'action, marqués par la revue à la baisse des objectifs quantitatifs à
atteindre et le report des délais fixés dans ce sens. En effet, l'horizon pour
l'éradication quasi-complète de l'analphabétisme, initialement fixé à 2015
par la stratégie d'alphabétisation et d'éducation non-formelle de 2004, a été
repoussé à 2029, conformément à la feuille de route adoptée par l'agence
en 2023.
En outre, la dimension territoriale n’a pas été intégrée dans les plans
stratégiques de l’agence, notamment à travers l’adoption de programmes
régionaux intégrés qui prennent en compte les disparités régionales en
termes d’analphabétisme, ainsi que les spécificités socio-culturelles de
chaque Région. Ces programmes régionaux devraient permettre
d’impliquer tous les acteurs dans les efforts de lutte contre
l'analphabétisme, et être traduits en plans d'action et projets tenant compte
des capacités d'exécution et des ressources disponibles au niveau
territorial.
Quant au financement des programmes de lutte contre
l'analphabétisme, il repose essentiellement sur les subventions de l'État,
qui ont représenté environ 84% des ressources totales de l'agence entre
2015 et 2023, suivi par le soutien de l'Union européenne qui a atteint 14%,
tandis que le total des contributions des conseils des régions, des
départements ministériels, des organisations de la société civile partenaires
et des institutions de coopération internationale n'a pas dépassé 2%.
Par ailleurs, le taux moyen des paiements n'a pas dépassé 29% du total des
dépenses engagées au cours de la même période. Cette situation est,
principalement, due aux retards des organisations de la société civile
partenaires dans la présentation des documents justificatifs et dans la
transmission à l'agence de la situation financière et comptable relative au
programme de lutte contre l'analphabétisme avant le versement des
tranches de soutien restantes. Cela a entrainé une accumulation des restes
à payer, qui se sont élevés à 584,58 MDH en 2022, soit environ 63% du
montant total des crédits de paiement au titre de la même année.
S’agissant de l'exécution et du contrôle des programmes de lutte
contre l'analphabétisme, il a été constaté l'absence d'un système de
classification des associations œuvrant dans le domaine d’alphabétisation,
qui permettrait de les inciter à se spécialiser et à s'organiser, d’une part, et
de faciliter l'évaluation de leur performance et la prise, au cours du


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              51
     processus de sélection, de décisions basées sur des informations précises,
     contribuant ainsi à garantir leur pérennité, d’autre part.
     La Cour a également relevé l'absence de mesures concrètes pour s’assurer
     de l’adéquation des espaces de formation proposés par les associations
     partenaires, ce qui pourrait impacter la qualité des formations dispensées,
     le degré d’attractivité pour les bénéficiaires et la rentabilité globale des
     projets. À cet égard, il a été observé que certains espaces de formation
     consistent en des appartements, des maisons résidentielles et des garages
     non aménagés pour accueillir des formations d’alphabétisation. Il convient
     de souligner, dans ce sens, que la proportion d’espaces publics dédiés à ces
     formations n’a pas dépassé 18% du total des lieux déclarés pour l'année
     scolaire 2022/2023.
     Dans le même contexte, il a été observé un faible taux de présence et
     d’assiduité des bénéficiaires des programmes d'alphabétisation dispensés
     par les organisations de la société civile. En effet, la moyenne de l'indice
     de présence a atteint environ 40% dans un échantillon de 14.263 classes,
     réparties sur 52 préfectures et provinces, inspectées sur le terrain par des
     bureaux d'études engagés à cet effet, durant la période 2019-2022. De
     même, la moyenne de l'indice d’assiduité dans la présence n'a pas dépassé
     43%, ce qui risque de limiter l'impact des efforts déployés pour lutter
     contre l’analphabétisme.
     En relation avec les mécanismes d'apprentissage dans le domaine de
     lutte contre l'analphabétisme, bien que plus de dix ans se soient écoulés
     depuis l'adoption des programmes pédagogiques pour la période 2009-
     2012, l'agence n'a pas encore procédé à l’actualisation de ces programmes.
     Cette situation résulte de l'absence de décisions claires quant aux
     modifications à apporter, notamment en ce qui concerne les compétences,
     les objectifs, les contenus et les approches pédagogiques relatives aux
     langues, aux mathématiques et aux sciences. Ces modifications sont
     essentielles pour répondre aux exigences d'équivalence avec les niveaux
     d'enseignement formel et la formation professionnelle, afin d’établir des
     passerelles entre les programmes d'alphabétisation et les autres systèmes
     éducatifs. De plus, le rythme d'adaptation de l'offre de formation des
     programmes d'alphabétisation aux besoins et spécificités des groupes
     cibles demeure insuffisant.
     À cet effet, la Cour a recommandé au Chef du gouvernement et à
     l'Agence de conclure un contrat-programme entre l'État et l'Agence afin
     de définir les objectifs stratégiques et quantitatifs à atteindre selon un
     calendrier approprié, ainsi que de mettre en place des mécanismes pour le
     suivi de la mise en œuvre des programmes et projets prévus, ainsi que




        Rapport annuel de la Cour des comptes au titre de 2023-2024
52                    - Principaux axes -
l’évaluation de leurs résultats et leur impact sur la réduction du taux
d'analphabétisme.
En outre, la Cour a recommandé à l'Agence d’améliorer l'efficacité et
l'efficience des programmes de lutte contre l'analphabétisme menés en
partenariat avec les organisations de la société civile, afin de renforcer leur
impact effectif sur la réduction du taux d'analphabétisme, notamment par
la classification des organisations actives dans ce domaine et l'adoption de
critères et procédures permettant de sélectionner des associations et des
coopératives sérieuses, disposant des ressources humaines spécialisées et
des compétences professionnelles nécessaires pour dispenser des
formations en alphabétisation.
Enfin, la Cour a recommandé, également, à l’Agence d'impliquer des
spécialistes dans la révision des programmes, des manuels et autres
supports pédagogiques, afin d'adapter l'offre de formation aux besoins et
spécificités des groupes cibles, tels que les personnes en situation de
vulnérabilité ou de handicap, les jeunes, les commerçants, les détenus, les
personnes souffrant d'analphabétisme fonctionnel, les parents et les
chômeurs.


        Chantier de réforme de la simplification des
         procédures et formalités administratives :
   Renforcer la gouvernance du chantier et accélérer la mise en
                      œuvre de ses projets

Le chantier de réforme de la simplification des procédures et formalités
administratives est basé sur une approche de transformation globale,
structurée autour de trois leviers d’action interconnectés et
complémentaires, qui portent sur l’inventaire, la transcription, la mise en
conformité et la publication des actes administratifs au niveau du portail
national « Idarati », puis l’enclenchement des chantiers de la simplification
et de la digitalisation des procédures et des formalités, et enfin, leur
traitement et leur délivrance dans un délai de 5 ans à compter du 28
septembre 2020, date d’entrée en vigueur de la loi n°55.19 relative à la
simplification des procédures et formalités administratives, soit avant la fin
du mois de septembre 2025.
À cet égard, les observations soulevées par la Cour, ont concerné
principalement les aspects relatifs aux étapes préparatoires à la mise en
œuvre de la réforme de la simplification des procédures administratives,
les mécanismes de la gouvernance, de pilotage et de la conduite du
changement au sein de l’administration, ainsi que le bilan de


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              53
     l’implémentation opérationnelle des nouvelles règles régissant les
     procédures administratives.
     Concernant le cadre stratégique et juridique de la réforme, durant la
     phase préparatoire de l’élaboration du projet de la loi n°55.19, précité, le
     diagnostic préalable des procédures et formalités administratives ne s'est
     pas appuyé sur une analyse approfondie de la situation des actes
     administratifs délivrés par l’ensemble des départements ministériels et
     établissements publics, leur degré de complexité, leurs délais de réalisation
     et leur conformité juridique. Ces limites ont entrainé plusieurs difficultés
     dans la déclinaison opérationnelle des mesures de la réforme, ainsi que le
     retard dans la mise en œuvre des chantiers structurants de réforme, dont la
     première étape relative à la transcription et à la publication des actes
     administratifs, n’a pu dépasser, à fin décembre 2023, 85% sur l’échantillon
     des 22 départements ministériels examinés.
     De même, l’adoption des textes réglementaires d’application prévus par les
     dispositions de la loi n°55.19 demeure inachevée. Il s’agit, notamment, de
     la non-publication des décrets relatifs à la définition et à l’élaboration des
     indicateurs afférents au traitement et à la délivrance des actes
     administratifs, aux modalités de gestion du portail national des procédures
     et formalités administratives ainsi qu’à la fixation de la liste des documents
     et pièces administratifs, nécessaires au traitement des demandes des actes
     administratifs, qu’il est possible de se procurer auprès des autres
     administrations au lieu d’exiger leur production par les usagers lors du
     dépôt des demandes. Ce retard a affecté le rythme de la déclinaison des
     chantiers stratégiques relatifs à l’interopérabilité entre administrations pour
     l’échange des pièces et documents administratifs, et sur le système de suivi
     des indicateurs de performance relatifs au traitement et à la délivrance des
     actes administratifs, ainsi que sur la gouvernance du portail « Idarati ».
     En ce qui concerne la gouvernance du chantier de la simplification des
     procédures et formalités administratives, il y a lieu de soulever la
     nécessité de renforcer son système par des instances techniques en vue de
     fédérer les chantiers de simplification et de digitalisation selon une
     approche participative, d’appuyer la Commission nationale de
     simplification des procédures et formalités administratives (CNSPFA)
     dans l’exercice de ses attributions et de l’assister dans l’opérationnalisation
     et le pilotage des projets stratégiques de la réforme. A cet égard, les parties
     prenantes se sont limitées à la création d’un seul comité technique dont le
     rôle est circonscrit dans l’instruction des répertoires des actes
     administratifs élaborés par les administrations et leur mise en conformité
     juridique en vue de les soumettre à la CNSPFA pour approbation sans pour
     autant assurer un suivi régulier de la mise en œuvre des chantiers



        Rapport annuel de la Cour des comptes au titre de 2023-2024
54                    - Principaux axes -
structurants de la réforme notamment celles de la simplification, de la
digitalisation et de l’interopérabilité.
Quant à la conduite et l’incitation au changement au sein des
structures administratives, elles ont été marquées par l’absence d’un plan
d’action national formalisé comprenant les principales étapes de la réforme
et permettant d’instaurer les leviers de changement nécessaires à la
concrétisation de ses transformations structurelles, incluant le
renforcement des capacités du personnel, l’échange des bonnes pratiques
et des approches méthodologiques nécessaires à la déclinaison des
chantiers ainsi que la pérennisation des acquis.
S’agissant du bilan de de la mise en œuvre des mesures opérationnelles
de la réforme de simplification administrative, il est à relever que les
départements ministériels et les établissements publics n’ont pas pu
achever l’opération préliminaire de formalisation, de transcription, de mise
en conformité juridique et de publication des procédures administratives
relevant de leurs compétences dans les dates butoirs fixées par les
dispositions législatives à fin Mars 2021. En effet, sur l’échantillon retenu
des 22 départements ministériels, le taux de transcription des actes
administratifs à fin décembre 2023 a été de 85% et leur taux de publication
se limite à 70%.
En outre, les services administratifs ont rencontré des difficultés pour le
respect des mesures et des délais légaux (un délai maximal de 60 jours) de
traitement des demandes et de délivrance des actes administratifs, à cause
de l’insuffisance de la coordination entre les structures administratives, de
l’absence d’une réingénierie des processus en vigueur ou encore du
manque de ressources humaines qualifiées. L’analyse des résultats de
l’étude d’effectivité des mesures de la simplification administrative,
effectuée par le ministère de la transition numérique et de la réforme de
l'administration (MTNRA) en 2021, a conclu que 26% des actes
administratifs demandés sur l’échantillon sélectionné n’ont pas été remis
dans les délais indiqués sur le portail « Idarati » (l’enquête a couvert un
échantillon de 2.358 actes administratifs demandés par des personnes
particulières et 207 par des entreprises). De même, la Cour a noté
qu’environ 25% des administrations examinées continuent d’alourdir les
procédures imposées aux usagers en exigeant la légalisation de signature,
la fourniture de copies conformes ou encore la fourniture de plus d’un
exemplaire contrairement aux règles édictées par les dispositions de
l’article 7 de la loi précitée.
En ce qui concerne la digitalisation et l’interopérabilité entre les
administrations publiques, outre l’absence d’un cadre juridique de
l’administration numérique conférant le caractère opposable aux


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              55
     prestations administratives numériques, l’opérationnalisation d’une
     interopérabilité effective demeure confrontée à l’absence des prérequis
     nécessaires à l’instauration d’un écosystème national d’échange de
     données entre administrations, qui passe principalement par l’amélioration
     de la maturité des registres de données, l’encadrement juridique et normatif
     de leurs règles de gestion, la standardisation de la nomenclature des
     données communes des registres et le renforcement de la gouvernance de
     la gestion des données au niveau des administrations.
     Eu égard à ce qui précède, la Cour a recommandé au chef de
     gouvernement et au MTNRA d’asseoir un cadre stratégique de la
     simplification administrative intégré et global selon une approche axée sur
     les résultats et veiller à l’implémentation de plans d’action pour le pilotage,
     l’exécution et le suivi des projets de simplification de procédures
     administratives au sein des départements ministériels, en détaillant les
     résultats escomptés ainsi que les indicateurs de performances et délais de
     réalisation associés pour une mobilisation efficace des parties prenantes.
     Elle a recommandé également de renforcer la gouvernance et le pilotage
     de la réforme par des organes techniques thématiques créés par la CNSPFA
     en vue de fédérer les chantiers de la simplification et de la digitalisation
     selon une approche participative. De même, elle a recommandé de mettre
     en place un plan d’action pour revoir et compléter la réglementation des
     procédures administratives en vue de mettre en conformité les actes
     administratifs exigés aux usagers par rapport aux dispositions de la loi de
     la simplification administrative.
     En outre, la Cour a recommandé au MTNRA de centrer les projets de
     simplification des procédures administratives sur le parcours réel de
     l'usager, à travers une réingénierie des processus afin d’optimiser les étapes
     d’interaction avec l’usager au lieu de l'approche conventionnelle
     unidirectionnelle axée sur l’acte administratif, et de cibler les parcours
     prioritaires comme ceux de l’investisseur ou ceux qui présentent une
     complexité, et particulièrement les plus utilisés et à forte incidence sur
     l’usager. Elle a aussi recommandé d’asseoir les prérequis nécessaires à la
     mise en œuvre d’une interopérabilité entre les systèmes d’informations des
     administrations, en veillant à améliorer la maturité digitale des registres
     des données, à déployer un cadre normatif pour la gestion des registres de
     données, à uniformiser la nomenclature des données et à développer les
     registres de références des données communes des usagers.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
56                    - Principaux axes -
    Projets de construction et d’aménagement des
     bâtiments judiciaires et administratifs par le
                ministère de la Justice :
 Améliorer la planification stratégique et les mécanismes de
                      suivi des projets

Depuis la publication de la Charte de la réforme du système judiciaire en
2013, le ministère de la Justice a réalisé plus de 69 projets de construction
et d’aménagement des infrastructures judiciaires et administratives, pour
un montant global d'environ 3,2 MMDH de dirhams. Ces projets
concernent, principalement, la construction du siège de l'institut supérieur
de la magistrature, de 4 complexes judiciaires (palais de justice), d’une
cour d'appel, de 18 tribunaux de première instance et section de la justice
de la famille, de 22 centres de juges résidents et une sous-direction
régionale, en plus de 6 projets d’aménagement et d’extension.
Dans ce cadre, la mission d’évaluation a porté sur la gestion des projets de
construction et d’aménagement des bâtiments judiciaires et administratifs
pour la période 2017-2023, notamment les aspects relatifs à la planification
stratégique, à la programmation, au financement, et au suivi-contrôle, ainsi
que la valorisation et l'exploitation des projets en vue d’assurer le bon
fonctionnement des services de la Justice.
Concernant le cadre stratégique et de gestion des projets, le ministère
ne dispose pas d'une stratégie officielle pour la mise en œuvre des
programmes de construction et d'aménagement des bâtiments judiciaires et
administratifs, comme en dispose le décret fixant les attributions et
l’organisation du ministère de la Justice (n°2.22.400 du 18 octobre 2022),
qui prévoit l’adoption, par la direction de l'équipement et du patrimoine,
d’une stratégie pluriannuelle visant la gestion, la conservation et l’entretien
du patrimoine et de veiller à la sécurité des bâtiments de l'administration
centrale, des tribunaux et des services déconcentrés. Cette situation a
généré des difficultés en termes de contrôle et de suivi des programmes
d'investissement, ainsi qu’en termes d'évaluation du bilan des réalisations
par rapport aux objectifs et délais fixés. Ceci est accentué par les risques
de manque de synergie et de chevauchement des programmes annuels
d’investissement couplés à l’insuffisance des crédits budgétaires qui leur
sont allouées.
Dans le même sens, il a été constaté l'absence de normes de référence
définissant le mode de gestion des projets, de manière à préciser les critères
de détermination de la nature et du nombre des projets programmés
annuellement, leur répartition géographique et les entités chargées de leur


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              57
     maîtrise d’ouvrage. En outre, le ministère n'a pas procédé à l'évaluation de
     l'expérience de la maîtrise d’ouvrage déléguée, bien que 40% des projets
     délégués aient connu des insuffisances dans leurs programmation et
     gestion.
     En matière d’évaluation de la performance et de la gestion axée sur les
     résultats, les contrats-programmes conclus avec les directions régionales
     se sont limités à la définition des programmes prévisionnels afférents à
     l'année suivante, sans procéder à la fixation des objectifs visés à moyen
     terme, des projets programmés, des ressources humaines et matérielles à
     allouer à chaque direction régionale, et des indicateurs de suivi, de contrôle
     et d'évaluation de la performance. Par ailleurs, la mise en œuvre du
     mécanisme intitulé « Dialogue de gestion avec les directeurs régionaux »
     s'est limité à la discussion de la programmation budgétaire annuelle, sans
     inclure l’appréciation de l’état d’avancement des projets programmés et
     l'identification, le cas échéant, des causes des retards dans leurs exécution.
     À cet égard, il convient de signaler que le taux d'exécution des programmes
     prévisionnels des directions régionales a connu une tendance à la baisse,
     passant de 49% à 47% entre 2017 et 2021, et ce à cause de l'accumulation
     de projets en retards ou en difficulté, et de la non priorisation de la
     résolution des problèmes techniques auxquels sont confrontés les projets
     en cours d’exécution avant de procéder à la programmation de nouveaux
     projets.
     En ce qui concerne le financement des projets, il a été constaté que la
     dimension régionale n'est pas intégrée dans la structure budgétaire du
     « Fonds spécial pour le soutien des juridictions ». En effet, les dépenses de
     ce Fond sont imputées de manière consolidée sous l'intitulé « services
     communs », ce qui génère des difficultés de suivi de l'exécution financière
     des projets, de collecte des données et d’établissement de tableaux de bords
     propres à chaque région.
     Dans le même ordre d’idée, l’efficacité de l'utilisation des crédits
     disponibles est à améliorer. En effet, le taux de report des crédits du
     « Fonds spécial pour le soutien des juridictions » dépasse 59% des crédits
     relatifs à la période 2017-2023. De même, le taux d'exécution des dépenses
     d'investissement du Budget général a varié entre 51% et 70% pendant la
     même période.
     Quant à l'accompagnement de la réalisation des projets de
     construction et d'équipement, des insuffisances ont été constatées en
     matière de régularisation de la situation juridique de plusieurs biens
     immobiliers. Cela est dû à l'absence d'une stratégie foncière proactive pour
     identifier et acquérir les lots à affecter à la construction des bâtiments
     judiciaires et administratifs, en plus de l'absence de critères définissant les


        Rapport annuel de la Cour des comptes au titre de 2023-2024
58                    - Principaux axes -
conditions d'évaluation de la viabilité des lots de terrains proposés par les
commissions compétentes et leur adéquation aux besoins du ministère.
L'exécution des projets est confrontée, également, à des difficultés
générant des retards dans leur achèvement. Ces retards sont dus aux
modifications apportées à la conception initiale des ouvrages à cause de
l’insuffisance de la qualité des études techniques préalables, ainsi qu’aux
difficultés survenus lors de l’exécution des travaux en parallèle avec la
mise en fonctionnement des services de justice souvent marqués par
l’importance des flux des usagers. Ainsi, le taux global de projets réalisés
dans les délais fixés n’a pas dépassé 11% pendant la période 2017-2022.
Concernant la valorisation des bâtiments judiciaires et administratifs,
il convient de préciser que 47% des bâtiments nécessitent des rénovations
majeures, car ils sont soit totalement inexploitables (14%), soit
partiellement exploitables (33%). Toutefois, le ministère ne dispose pas
d'un plan d’action, pour la mise à niveau desdits bâtiments, permettant
d'évaluer leur état et de procéder à leur réhabilitation. De même, le
patrimoine du ministère comprend, également, des bâtiments anciens non-
exploités (bâtiments judiciaires et administratifs et logements de fonction),
mais il ne dispose pas d’une vision quant à leur usage.
Eu égard à ce qui précède, la Cour a recommandé au ministère de la
justice d’élaborer une stratégie officielle pour la préparation et la mise en
œuvre de programmes de construction et d'aménagement des bâtiments
judiciaires et administratifs, en précisant ses objectifs, le calendrier de sa
réalisation, les sources de financement et les parties concernées ; et
d’adopter des plans d’action conformes aux normes de la nouvelle
organisation judiciaire. Elle a également recommandé de mettre en place
un mécanisme pour évaluer la qualité des études techniques préalables, afin
de prévenir les modifications récurrentes des plans initiaux de conception
des ouvrages après le démarrage des projets.
De même, la Cour a recommandé d'adopter une stratégie immobilière
proactive pluriannuelle pour l'acquisition de terrains avant de commencer
la construction des ouvrages, et d'établir un plan d’action pour l’entretien
et la réhabilitation des bâtiments inadaptés, ainsi que la mise en place des
infrastructures nécessaires au bon fonctionnement des services de la
justice.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              59
                                    Contrôle de la gestion

                                             Secteurs financiers

                                                Finances publiques :
                                                       Points d’attention

     L’année 2023 a été caractérisée, au niveau international, par la continuité
     des tensions géopolitiques, avec leurs répercussions sur la situation
     économique mondiale. Ainsi, après les signes de reprise des effets négatifs
     de la pandémie du Covid-19 pendant l’année 2021, le contexte
     international a été marqué, à partir de 2022, par une période de manque de
     visibilité chez les acteurs économiques, ce qui a conduit à un
     ralentissement continu du rythme de croissance des différentes économies
     du monde et l’augmentation des pressions inflationnistes ayant conduit au
     resserrement des politiques monétaires. Même si le début de l’année 2024
     a montré un certain soulagement dans cette situation, l’état d’instabilité
     résultant des récents développements du conflit au Moyen-Orient laisse
     présager une situation difficile, notamment compte tenu des fluctuations
     que pourraient connaître les prix de l’énergie.
     Au niveau national, l'année 2023 a connu la poursuite du phénomène de
     sécheresse et ses effets négatifs sur le secteur agricole et ses répercussions
     sur l'économie nationale, qui a connu un taux de croissance ne dépassant
     pas les 1,5% en 2022 et 3,4% en 2023. Au cours de l'année 2024, ce taux
     ne devrait pas dépasser 2,5%, selon les prévisions du Haut-Commissariat
     au Plan, et 2,8%, selon les estimations de la Banque Al Marghrib.
     L'accentuation du problème du stress hydrique, et les investissements
     importants et urgents requis pour l’atténuer, ont conduit au lancement du
     Programme national d'approvisionnement en eau potable et en eau
     d'irrigation, couvrant la période 2020-2027, et doté d'un budget de
     143 MMDH.
     De même, les dégâts provoqués par le séisme d’Al Haouz, en septembre
     2023, ont ajouté un défi supplémentaire, appelant à la mobilisation
     d’importantes ressources pour financer la reconstruction et aider les
     personnes touchées. A cet égard, 9,5 MMDH ont été dépensés dans le cadre
     des aides aux habitants, dont 4,75 MMDH sous forme d’aide directe aux
     ménages, jusqu’au 25 octobre 2024, selon le communiqué diffusé suite au
     conseil du gouvernement du 7 novembre 2024. En outre, en exécution des
     Hautes Instructions Royales, il a été décidé de prolonger le versement de


        Rapport annuel de la Cour des comptes au titre de 2023-2024
60                    - Principaux axes -
l’aide directe pour une période supplémentaire de 5 mois. De même, dans
le cadre du programme de reconstruction et de réhabilitation général des
zones sinistrées, couvrant la période 2024-2028, des chantiers sectoriels
ont été également lancés dans ces zones.
Par ailleurs, l’organisation par le Maroc de la Coupe du Monde du football
en 2030 (conjointement avec l'Espagne et le Portugal), ainsi que la Coupe
d'Afrique des Nations en 2025, constitue un défi important qui nécessite la
mobilisation d’importantes ressources pour financer les investissements
majeurs nécessaires à la mise à niveau des infrastructures sportives,
touristiques, de communication, de transport, etc.
Dans le contexte de ces contraintes et défis, les grandes réformes engagées
par notre pays se poursuivent, notamment la réforme du système de
protection sociale qui devrait, selon les dernières estimations du ministère
de l'Economie et des Finances, coûter 53,5 MMDH, lorsque tous les
mécanismes de protection sociale seront activés en 2026, dont
38,5 MMDH à financer sur le budget de l'Etat. En matière
d'investissement, la tendance actuelle est de maintenir l'effort
d'investissement public, notamment à travers les dépenses d'investissement
portés le budget général de l'Etat, qui sont passées de 52,3 MMDH en 2015
à 119,2 MMDH en 2023. Cette tendance est appelée à se poursuivre au
même niveau au cours des années à venir, selon les données de la
programmation budgétaire triennale pour la période 2024-2026. Ceci
nécessite le développement des mécanismes nécessaires favorisant l’effet
de levier de l’investissement public.
Tous ces facteurs sont de nature à augmenter la pression sur les finances
publiques et à poser des défis réels à l’atteinte des objectifs fixés,
notamment dans le cadre de la programmation budgétaire triennale, qui
envisage un retour progressif à l'équilibre des finances publiques. Ainsi, au
niveau du déficit budgétaire, qui a connu une relative amélioration en 2023,
puisqu'il est revenu à 4,4% du produit intérieur brut contre 5,4% en 2022,
l'objectif est de revenir progressivement à un taux de déficit de l'ordre de
3% à l’horizon 2026. Quant à la dette du Trésor, elle devrait être
progressivement réduite pour atteindre 66,3% du produit intérieur brut en
2027, selon le rapport sur l'exécution du budget et le cadre
macroéconomique accompagnant le projet de loi de finances pour l’année
2025. Il va sans dire que l’atteinte de ces objectifs demeure liée aux
performances économiques, notamment en termes de croissance du produit
intérieur brut et de son impact sur les ressources de l’État et la pérennité de
leur taux de croissance.
À cet égard, les ressources, notamment les recettes fiscales, ont connu une
croissance significative, en relation avec la réforme fiscale initiée à partir


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              61
     de 2022, en plus d'autres facteurs tels que le taux d'inflation élevé et son
     impact sur les recettes douanières en particulier. Ainsi, les recettes fiscales
     ont connu une augmentation de 17,4% entre les années 2021 et 2022, avant
     que le rythme de leur augmentation ne diminue à environ 5,6% entre les
     années 2022 et 2023. L'année 2024 (jusqu'à fin août), enregistre une
     augmentation de 11,7% par rapport à la même période en 2023.
     En ce qui concerne les ressources, la réforme enclenchée dans le secteur
     des établissements et entreprises publics (EEP) et au niveau du système
     d'investissement, sont de nature à atténuer la pression sur les finances
     publiques. En effet, la réforme des EEP favoriserait la réduction des
     transferts du budget de l'État au profit de ces derniers, ayant dépassé
     65 MMDH en 2023 et le développement de leurs contributions au budget
     de l'État qui n’a pas dépassé 16,8 MMDH au titre de la même année. De
     même, l'augmentation de la part de l'investissement privé, que vise la
     réforme de l’investissement, réduirait la charge que constitue
     l'investissement public en plus des recettes fiscales qu'il pourrait générer.
     Par ailleurs, la rationalisation des dépenses constitue un levier important à
     même de contribuer à offrir les marges budgétaires nécessaires, à travers
     une définition précise des priorités, une orientation optimale des dépenses
     et une rationalisation de leur utilisation, d'autant plus que ces dépenses ont
     connu une augmentation continue ces dernières années, notamment au
     niveau des dépenses ordinaires de l'État qui ont progressé de plus de 33 %
     au cours de la période de 2020 à 2023.
     Les réformes, précitées, peuvent offrir des marges intéressantes pour
     répondre aux besoins de financement, néanmoins, pour atteindre cet
     objectif, il s’avère cruciale d’accélérer leur mise en œuvre pour mobiliser
     les ressources nécessaires à temps, ainsi que pour établir des sources de
     financement stables et chercher d’autres solutions novatrices de
     financement pour réduire les pressions sur les finances publiques.
     Dans le même contexte, il apparaît urgent de prévoir des marges
     supplémentaires pour faire face aux situations d’urgence et aux
     circonstances exceptionnelles, dont la fréquence a considérablement
     augmenté ces dernières années, en relation principalement avec les
     phénomènes résultant du changement climatique (telles que les sécheresses
     et les inondations), les conditions géopolitiques instables, les crises
     sanitaires, etc.
     Concernant les risques potentiels auxquels les finances publiques
     pourraient être confrontées à moyen et long terme, la Cour réaffirme la
     nécessité urgente d'engager et d'accélérer la réforme du système de retraite,
     afin de préserver sa viabilité, tout en attirant l'attention sur la situation
     préoccupante de la Caisse marocaine de retraite, qui a enregistré un déficit


        Rapport annuel de la Cour des comptes au titre de 2023-2024
62                    - Principaux axes -
technique de 9,8 MMDH, à fin 2023, ce qui entraîne une baisse de ses
fonds de réserve à 65,8 MMDH, et conduirait à leur épuisement en 2028,
selon les données du ministère de l'économie et des finances.


     Programmation des dépenses du budget de
                    l’Etat :
    Dépenses de fonctionnement en augmentation et dépenses
   d’investissement exigeant l’amélioration de la détermination
           des priorités et la pré-évaluation des projets

La loi organique n°130.13 relative à la loi de finances a établi de nouvelles
règles de programmation et d’exécution du budget de l’Etat. Ces règles
reposent sur trois piliers, en l’occurrence le renforcement des principes
financiers, de la transparence et de la lisibilité budgétaire, l’accroissement
du rôle du Parlement dans le débat budgétaire et le renforcement de la
performance de la gestion publique.
La Cour des comptes a examiné la gestion des dépenses de l’Etat (Budget
général, comptes spéciaux du Trésor et services de l’Etat gérés de manière
autonome), sur la période 2015-2022, en se focalisant sur l’appréciation de
la phase de la programmation budgétaire et la planification des dépenses
publiques. Un échantillon de quatre départements dépensiers importants a
été choisi, eu égard à leurs enjeux budgétaires, en l’occurrence les
départements de la santé, de l’équipement, de l’éducation nationale et de
l’agriculture. Pour sa part, l’examen des systèmes d’information a porté sur
les deux systèmes d’information clés qui encadrent la programmation et le
suivi d’une grande partie de ces dépenses, en l’occurrence e-budget 2 et
GID.
En ce qui concerne l’évolution des dépenses de l’Etat, il a été noté que,
sur la période 2015-2022, les dépenses de l’Etat n’ont cessé de croître
enregistrant une augmentation globale d’environ 224 MMDH, soit une
évolution de 60,3%. L’analyse de la structure de ces dépenses montre que
celles du personnel constituent le principal poste budgétaire, suivi de
l’encours de la dette du Trésor et de la charge de la compensation. La
tendance haussière de ces dépenses à caractère incompressible continue de
peser sur les finances publiques en réduisant les marges de manœuvre lors
de la programmation budgétaire.
Quant à la précision des prévisions macroéconomiques, l'amélioration
de la qualité de la programmation budgétaire triennale reste tributaire de
l'amélioration de la qualité des prévisions qui sous-tendent cette


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              63
     programmation, incluses dans les documents budgétaires soumis au
     Parlement, et qui sont toujours limitées à l'année n+1. En outre, ces
     prévisions ne fournissent qu’une évaluation qualitative des hypothèses
     retenues et dans quelle mesure leur évolution affecte la programmation.
     Dans ce sens, il convient de souligner que les propositions issues du
     processus de programmation ne s'appuient pas nécessairement sur le
     contenu des stratégies sectorielles.
     S’agissant du processus budgétaire, il a été noté le manque de précision
     des rôles et des responsabilités des intervenants dans la programmation et
     la gestion budgétaire, en raison du faible encadrement de la mise en œuvre
     de certaines règles budgétaires établies par la loi organique de la loi de
     finances, notamment la non définition préalable des conditions de
     détermination des cas urgents et inattendus d'intérêt public qui régissent le
     recours à l'ouverture de crédits supplémentaires au cours de l'année, ainsi
     que la manière d'évaluer la situation économique et financière qui pourrait
     nécessiter le gel de l'exécution de certaines dépenses d'investissement, ce
     qui affecterait la qualité du processus de programmation de ce type de
     dépenses.
     Pour ce qui est du dispositif de pilotage et de suivi de la mise en œuvre
     du chantier de performance, il a été noté, que l’articulation de la
     démarche de performance avec la réalité de la gestion des dépenses est un
     processus qui nécessite des améliorations à plusieurs niveaux. Les
     dispositifs de performance proposés dans les projets de performance ne
     constituent qu’une première ébauche à améliorer à travers, notamment, le
     déploiement effectif du contrôle de gestion au niveau des départements
     ministériels, l’amélioration de l’accès aux données et la mise à niveau des
     systèmes d’information.
     Concernant les systèmes d’information, il convient de souligner que,
     malgré les gains en efficacité et fiabilité qu’ils ont apportés dans la
     production de la documentation budgétaire, ils restent à compléter par des
     outils adaptés et mutualisés portant, essentiellement, sur la mise en place
     de systèmes d’information répliqués au niveau des départements
     ministériels pour améliorer les travaux de préparation des programmes, et
     la déclinaison du processus de suivi, de pilotage et de reporting de la
     performance.
     Au niveau de la programmation des dépenses d’investissement, il a été
     noté que malgré la tendance légèrement baissière que connait les reports
     de ces crédits, passant de 17,3 MMDH entre 2014 et 2015 à 11,4 MMDH
     entre 2021 et 2022, leur montant demeure important et représente environ
     13 % des crédits de paiement relatifs à la loi des finances pour l’année
     2022.


        Rapport annuel de la Cour des comptes au titre de 2023-2024
64                    - Principaux axes -
En outre, l’absence d’estimation systématique des charges récurrentes des
projets d’investissement, pour leur prise en compte dans la programmation
et la budgétisation, risque de compromettre la mise en exploitation des
projet achevés, leur productivité et d’affecter la durabilité des actifs créés,
faute de leur entretien et maintenance.
Par ailleurs, les méthodes de sélection des projets demeurent non
définies. En effet, au niveau des départements ministériels, en l’absence
d’une méthodologie clairement définie et standardisée, les propositions de
projets sont généralement présentées dans des fiches de projets
partiellement renseignées, accompagnées éventuellement des études
réalisées. Les critères de programmation des projets ne débouchent pas sur
leur hiérarchisation par priorité. Aussi, les projets d'investissement ne sont
pas systématiquement soumis à des analyses de coûts-avantages ou de
coûts-efficacité. Ceci nécessite une meilleure maîtrise des besoins et
l’utilisation d’indicateurs permettant de renseigner sur la situation des
secteurs et des départements et servant à la fixation des priorités et
l’orientation des choix en matière d’investissement.
Enfin, il a été soulevé que malgré les efforts déployés pour sa
concrétisation, le projet de l’implémentation de la banque de données des
projets et la mise en place d’un cadre unifié et cohérent de gestion facilitant
la programmation des dépenses d’investissement est toujours en cours de
mise en œuvre.
Eu égard à ce qui précède, la Cour a recommandé au ministère de
l’économie et des finances d’œuvrer à la maîtrise des dépenses,
notamment, celles du personnel, de la dette du trésor et de la charge de
compensation pour disposer de plus de marges de manœuvre lors de la
programmation budgétaire, d’œuvrer à l’amélioration des prévisions
budgétaires au niveau de la Programmation budgétaire triennale en vue de
réhausser sa qualité, ainsi que l’encadrement des règles liées au recours
aux crédits supplémentaires et au gel des investissements en précisant les
conditions de recours à leur utilisation.
La Cour a recommandé, également, d’instaurer une formalisation
adéquate des échanges entre les différents acteurs de la programmation
budgétaire et de clarifier le rôle de chacun d’entre eux en le précisant
davantage au niveau de la charte de gestion prévue par la circulaire du Chef
du Gouvernement relative au rôle et aux attributions du responsable de
programme ainsi que de continuer l’implémentation de la démarche de
performance à travers notamment le contrôle de gestion, la disponibilité
des données de qualité et la mise en connexion des systèmes d’information.
Enfin, la cour a recommandé d’améliorer la programmation des dépenses
d’investissement à travers plus de maîtrise des reports de crédits,


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              65
     l’estimation systématique des charges récurrentes des projets
     d’investissement pour leur prise en compte dans la programmation et la
     budgétisation.


                            Certification des comptes de l'État :
                 Mission conditionnée par les contraintes du passage
                             à la comptabilité générale

     La certification des comptes de l'Etat s'inscrit dans le cadre de la mise en
     œuvre des dispositions de la Constitution de 2011 dans le domaine de la
     consolidation et la protection des principes et valeurs de bonne
     gouvernance, de transparence et de reddition des comptes de l'Etat et des
     organismes publics. Ces principes ont été transcris dans la loi organique
     relative à la loi de finances de 2015. La certification des comptes de l’Etat
     est l'une des dispositions entrées en vigueur à partir de l'année 2020. Elle
     constitue un chantier stratégique de grande importance dans le processus
     de modernisation de la gestion des finances publiques, à même de
     contribuer au renforcement de la fiabilité et de la transparence des comptes
     de l'État, leur crédibilité vis-à-vis du citoyen, des investisseurs et des
     institutions internationales.
     Ce chantier est directement lié à la transformation majeure que représente
     le passage de la comptabilité de caisse à la comptabilité en droits et
     obligations constatés à partir des comptes de 2018. Il constitue un grand
     défi pour les entités chargées de tenir cette comptabilité, compte tenu de sa
     nature, fondamentalement différente de la comptabilité de caisse dont
     l’usage a été consacré pendant plusieurs décennies. Une telle différence
     s’aperçoit, à titre d’exemple à travers le nombre d’opérations comptables
     dépassant 300 millions de ligne par exercice, ainsi qu’à travers la
     multiplicité des acteurs de la comptabilité générale, constitués d'environ
     700 comptables publics et 1 800 ordonnateurs et sous-ordonnateurs. Par
     conséquent, la mission de certification des comptes de l'État dépend des
     progrès à réaliser en matière de tenue de la comptabilité générale, de la
     qualité des comptes et de la mise à disposition d'informations et de données
     permettant à la Cour des comptes de les certifier conformément aux normes
     d’audit financier et dans des délais raisonnables pour éviter le cumul des
     exercices à certifier.
     Pour atteindre l'objectif de certification des comptes de l'État, les efforts se
     sont poursuivis au niveau des entités chargées de la tenue de la
     comptabilité, ainsi qu'au niveau de la Cour des comptes, qui a pris plusieurs
     initiatives depuis 2017 et a réalisé un ensemble de travaux en partenariat
     avec la Trésorerie Générale du Royaume, en sa qualité de producteur des


        Rapport annuel de la Cour des comptes au titre de 2023-2024
66                    - Principaux axes -
comptes, ainsi qu'avec les autres intervenants en matière de tenue de la
comptabilité de l'Etat, afin de pouvoir mener la mission de certification
dans de bonnes conditions conformément aux normes professionnelles et
dans des délais raisonnables.
Par ailleurs, la Cour a rappelé à plusieurs reprises, notamment dans ses
rapports annuels et dans ses rapports relatifs à l'exécution de la loi de
finances, les initiatives entreprises pour réussir ce chantier ainsi que
l’approche basée sur l’accompagnement et la progressivité qu’il a adoptée
en tenant compte des défis et des contraintes liés à la tenue de la
comptabilité générale. Elle a également attiré l'attention sur la nécessité
d'une forte implication de tous les intervenants dans ce chantier (les
ordonnateurs, la Trésorerie générale du Royaume, les comptables publics,
…) ainsi que le besoin de développer le travail en commun entre ces
acteurs afin d’assurer les conditions nécessaires à son succès et dépasser
les contraintes qui compromettent la réalisation de la mission de
certification des comptes de l’État au titre des exercices 2020, 2021 et
2022.
Il est à noter que, dans le cadre de la production des comptes, la Cour a
reçu de la Trésorerie Générale du Royaume le 5 septembre 2023, le grand
livre des exercices 2020 et 2021, complétant les éléments précédemment
communiqués des deux comptes généraux de l’État pour les mêmes
exercices produits respectivement le 27 mai 2022 et le 23 février 2023.
La Cour a également reçu le 21 mars 2024 les premiers éléments du compte
général de l’Etat au titre de l’exercice 2022, accompagnés de certains
documents récapitulatifs. Ainsi, les premiers travaux de certification des
comptes de l’État au titre de l’exercice 2020 (y compris les soldes
d’ouverture) et l’exercice 2021 ont démarré, à partir du 13 décembre 2023.
Si le processus de certification des comptes de l’Etat a enregistré quelques
points positifs, matérialisés principalement par les progrès enregistrés au
niveau des informations et documents communiqués par la Trésorerie
Générale du Royaume, toutefois, certaines contraintes impactent toujours
l’avancement normal de la mission. Il convient de noter que pour évoluer
progressivement vers des délais raisonnables de certification des comptes
de l'État conformément aux normes internationales et aux bonnes
pratiques en la matière, il est important de mettre en place un système
de contrôle interne efficace et des procédures d'échange et d'accès
continu aux informations et aux données en toute sécurité et en temps
opportun auprès de la Trésorerie générale du Royaume, des
comptables publics et des ordonnateurs concernés.




                                         Rapport annuel de la cour des comptes au titre de 2023-2024
                                                      - Principaux axes -                              67
                                                 Secteurs sociaux


                                                       Santé mentale :
              Des besoins croissants qui nécessitent la révision de son
                                      système

     L’Enquête Nationale de Prévalence des Troubles Mentaux (2003-2006),
     menée auprès de la population âgée de 15 ans et plus, a révélé que ces
     troubles constituent une charge pathologique importante et représentent un
     enjeu majeur de santé publique. Ce constat a provoqué une prise de
     conscience accrue de l’ampleur du problème et a donné lieu à l’adoption
     de plusieurs stratégies nationales dans ce domaine.
     La mission de contrôle de la Cour avait pour objectif de s’assurer que le
     système de santé mentale, dans ses différentes dimensions, est en mesure
     de répondre de façon adaptée aux besoins de la population. Elle a abordé,
     notamment, les aspects portant sur la prévention en matière de santé
     mentale, la disponibilité et l’accessibilité de l’offre de soins, ainsi que sur
     les conditions de prise en charge des malades.
     Concernant les aspects relatifs à la promotion et la prévention, il a été
     constaté que ces éléments sont insuffisamment appréhendés dans le
     système de santé mentale, au regard des préconisations de l’Organisation
     Mondiale de la Santé. En effet, quoique les stratégies dédiées à la santé
     mentale accordent une place importante à la promotion et la prévention, les
     efforts déployés par le Ministère de la Santé et de la Protection sociale
     (MSPS) dans ce cadre restent insuffisants, aussi bien envers l’ensemble des
     citoyens qu’envers des populations spécifiques. Ces insuffisances en
     matière de prévention des troubles mentaux peuvent entraîner des prises en
     charge médicales coûteuses pour le système de santé national.
     Au niveau de l’offre de soins dans le domaine psychiatrique, et bien
     que des efforts aient été déployés par le MSPS durant les dernières années
     pour le développement d’une offre de soins adaptée, ces efforts restent
     encore insuffisants pour garantir la disponibilité des établissements de
     santé mentale et l’accessibilité suffisante de ces soins à l’ensemble de la
     population. À cet égard, la Cour a révélé l’insuffisance des infrastructures
     sanitaires et leur non généralisation à l’échelle nationale. Elle a également
     relevé l’insuffisance des médecins spécialistes, leur répartition inégale et
     le manque de certains profils spécialisés dans la prise en charge des patients
     atteints de troubles mentaux. De plus, il a été constaté la non disponibilité
     des médicaments au niveau des structures de soins, ainsi que l’insuffisance


        Rapport annuel de la Cour des comptes au titre de 2023-2024
68                    - Principaux axes -
des taux de remboursement de certains médicaments et actes médicaux par
l’assurance maladie.
Concernant la prise en charge et l’organisation des soins et services de
santé, la Cour a noté plusieurs insuffisances liées particulièrement à la
faible intégration de la santé mentale dans les établissements de soins
primaires, au manque d’articulation entre les différents niveaux de soins
psychiatriques et à l’absence d’une prise en charge globale des patients.
Ces insuffisances engendrent des ruptures dans les parcours de soins,
dommageables pour les patients et exercent une pression supplémentaire
sur les structures hospitalières. La Cour a également relevé la discontinuité
des soins à cause du manque de dispositifs de suivi post -hospitalisation,
ainsi que l’insuffisance des établissements intermédiaires de réhabilitation
et des structures d’accueil des cas sociaux.
Eu égard à ce qui précède, la Cour des comptes a recommandé
au Chef du gouvernement de développer une politique intégrée avec
des orientations claires prenant en compte les grands enjeux de ce système,
notamment ceux relatifs à la promotion de la santé mentale, à la prévention
des maladies mentales et au développement d'une offre de soins adaptée et
répondant aux besoins de la population. Elle a également recommandé
d’adopter un cadre juridique adapté tenant compte de la spécificité de la
santé mentale, et un cadre de gouvernance favorable qui implique
l’ensemble des parties prenantes.
En outre, le Cour a recommandé au ministère de la Santé et de
la Protection sociale d’élaborer et de mettre en œuvre une stratégie
multisectorielle appropriée en matière de santé mentale, fondée
principalement sur l’élaboration et la mise en œuvre d’une stratégie de
renforcement de la prévention, le renforcement de l'offre de soins dédiée
ainsi que l’utilisation optimale des ressources disponibles. Elle a, enfin,
recommandé de se doter de dispositifs de surveillance et de veille
épidémiologique, en se basant sur un système d’information efficace et
harmonisé.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              69
                                   Généralisation du préscolaire :
              Des progrès tangibles avec la nécessité de pérenniser le
                               modèle en vigueur

     La mission de contrôle réalisée par la Cour des comptes relative à
     l’enseignement préscolaire a abordé, principalement, les stratégies et
     programmes mis en œuvre par le ministère en charge de l’enseignement
     préscolaire, sur la période 2000-2023, dans le but de concrétiser la vision
     de la généralisation et du développement du préscolaire. La mission a
     également examiné le degré d’atteinte des objectifs du programme national
     de généralisation et de développement du préscolaire (PNGDEP : 2018-
     2028), ainsi que la gouvernance et la gestion actuelles de l’enseignement
     préscolaire, en particulier dans le secteur public.
     Concernant les stratégies et programmes du ministère, il a été constaté
     l’existence d’une vision claire pour le préscolaire sans qu’elle soit,
     toutefois, suffisamment traduite au niveau de ces stratégies. En outre, les
     programmes du ministère n’ont pas concrétisé les objectifs de la Charte
     nationale d’éducation et de formation et de la vision stratégique 2015-
     2030, ce qui n’a pas permis d’atteindre les objectifs fixés par ces deux
     documents, notamment en matière d’intégration du préscolaire dans le
     primaire, de l’obligation de cette phase d’enseignement, et de
     l’élargissement de l’offre préscolaire du secteur privé. En outre, les
     programmes et stratégies du préscolaire n'ont pas bénéficié d'un suivi et
     d’un pilotage appropriés lors de leur mise en œuvre.
     La Cour a également relevé que la réalisation de l’objectif de généralisation
     du préscolaire s’est focalisée sur l’augmentation de l’offre publique, sans
     impliquer le secteur privé dans les différents programmes et stratégies
     visant le préscolaire et sans mettre en place des mesures pour encourager
     ce dernier à élargir son offre pédagogique.
     Concernant l’élaboration et la mise en œuvre du programme national
     de généralisation et de développement du préscolaire 2018-2028
     (PNGDEP), des résultats encourageants, par rapport aux objectifs tracés,
     ont été enregistrés dans l’optique de la généralisation du préscolaire.
     Néanmoins, ce programme s’est focalisé exclusivement sur le
     développement de l’offre éducative publique à travers la construction et
     l’équipement des salles de classe dans le préscolaire public, sans prendre
     suffisamment en compte les autres objectifs prévus dans la vision
     stratégique.
     S’agissant de la gouvernance et de la gestion du préscolaire public, il a
     été relevé la non intégration du préscolaire dans le cycle primaire comme



        Rapport annuel de la Cour des comptes au titre de 2023-2024
70                    - Principaux axes -
prévu par la Charte nationale d’éducation et de formation, la Vision
stratégique 2015-2030 et le PNGDEP. Le ministère s’est principalement
limité à l’intégration pédagogique, en raison du choix de la méthode de
gestion indirecte du préscolaire public.
La Cour a, par ailleurs, noté l’attribution de la gestion des classes à
certaines associations, reconnues pour leur compétence dans le secteur du
préscolaire. Toutefois, ce modèle de gestion qui présente plusieurs
avantages, notamment sur le plan budgétaire, comporte certains risques
pouvant impacter la pérennité du préscolaire public à moyen et long terme,
surtout avec l’augmentation significative de l’effectif des éducateurs.
En ce qui concerne les infrastructures, les équipements et la formation des
ressources humaines dédiées au préscolaire, il a été noté des cas de non-
respect des critères de création des unités du préscolaire, un manque
d’équipements et une insuffisance des investissements dans la formation
des éducateurs, et ce, malgré les efforts consentis par le ministère à la fois
sur les plans pédagogique et budgétaire pour leur garantir une formation
adéquate.
Eu égard à ce qui précède, la Cour a recommandé au ministère de
l'éducation nationale, du préscolaire et des sports, d’améliorer le processus
de planification stratégique du préscolaire à travers, notamment,
l’harmonisation de ses stratégies et programmes avec la vision et les
objectifs visés par la Charte nationale d’éducation et de formation et la
vision stratégique 2015-2030, ainsi que d’établir un diagnostic approfondi
et mis à jour de la situation du préscolaire en s’appuyant sur des données
précises et fiables.
Elle a également recommandé d’apporter les améliorations nécessaires
aux éléments et composantes du PNDGEP en traduisant, notamment, les
objectifs relatifs à la réhabilitation du préscolaire non structuré et la
promotion du secteur privé en mesures et actions opérationnelles, chiffrées,
précises et mesurables, ainsi que de mettre en place des solutions
alternatives pour optimiser l’usage des salles du préscolaire et éviter leur
sous exploitation.
Enfin, la Cour a recommandé d’améliorer la gouvernance et la gestion
du préscolaire public, notamment, à travers la mise en place des mesures
nécessaires pour garantir sa pérennité pédagogique, administrative et
financière, en harmonisant les conventions d’attribution directe des classes
avec les textes en vigueur et en intégrant le préscolaire et le primaire en
vue de constituer le cycle de l’enseignement primaire.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              71
                        Système de contrôle et de régulation de
                           l’enseignement supérieur privé :
        Améliorer l’efficacité du système pour un développement du
                                    secteur

     Le secteur de l’enseignement supérieur privé (ESP) a connu un
     développement significatif, avec un nombre d’établissements privés
     atteignant 196 établissements pour l’année académique 2022/2023, dont
     67 rattachés à 10 universités privées.
     La mission de contrôle réalisé par le Cour, qui a concerné la période 2010-
     2022, a abordé principalement le cadre général de l’ESP, la conception et
     le déploiement, du système de contrôle et de régulation de l’ESP, ainsi que
     la mise en œuvre effective du système de contrôle et de régulation par le
     ministère de tutelle.
     Concernant le cadre général de l’ESP, le secteur a connu ces deux
     dernières décennies des progrès significatifs tant en termes de nombre
     d’étudiants inscrits (de 10.146 en 2000 à 66.817 en 2023), que de la
     structure des établissements qui ont adopté le modèle d’"universités
     privées", de diversité des filières enseignées, de la reconnaissance par l'État
     de certains établissements, ainsi que de la concrétisation des partenariats
     entre des établissements d’ESP et l’État. Cependant, malgré ces évolutions
     notables sur les plans quantitatif et qualitatif, il a été constaté un
     ralentissement du rythme de la croissance annuelle du nombre d'étudiants
     inscrits durant la dernière décennie. En effet, le taux de croissance annuelle
     moyen (TCAM) a atteint +13%, pendant la période 2000-2010, alors qu’il
     n’a pas dépassé +5% pendant la période 2010-2023.
     Par ailleurs, il a été noté que l’ESP ne fait pas l’objet d’une vision claire ni
     d’une stratégie avec des objectifs spécifiques, traduits en plans d’action,
     révisés et évalués de manière périodique.
     Concernant la conception et le déploiement du système de contrôle et
     de régulation de l’ESP, ce système présente des écarts par rapport aux
     bonnes pratiques internationales. A titre d’exemple, l’Agence Nationale
     d’Evaluation et d’Assurance Qualité de l’enseignement supérieur et de la
     recherche scientifique (ANEAQ) est soumise à la tutelle administrative du
     ministère chargé du secteur et son rôle au niveau de l’ESP reste
     principalement consultatif, ne comprenant pas les prérogatives d’octroi ou
     de retrait des autorisations, de l’accréditation et de la reconnaissance des
     établissements d’ESP.
     En outre, le cadre juridique régissant l’ESP reste incomplet et peu adapté
     aux nouvelles réalités du secteur. En effet, plusieurs textes d’application


        Rapport annuel de la Cour des comptes au titre de 2023-2024
72                    - Principaux axes -
ne sont pas encore adoptés, tandis que d’autres ne couvrent pas tous les
aspects nécessaires. En outre, le cadre actuel de partenariat entre l’État et
certains établissements d’ESP nécessite davantage d’éclaircissement.
Par ailleurs, le système de régulation et de contrôle de l’ESP n’est pas
couvert par un système d’information global et intégré, capable d’assurer
une couverture globale du secteur et de garantir le contrôle efficace des
établissements.
Concernant la mise en œuvre du système de contrôle et de régulation
de l’ESP, elle connaît plusieurs insuffisances qui limitent son efficacité
pour assurer l’encadrement du secteur, son suivi de manière appropriée,
ainsi que son développement et le renforcement de sa qualité et de son
attractivité. Ces insuffisances touchent les principales phases de mise en
œuvre du système de contrôle et de régulation. En effet, celui-ci ne permet
pas d’assurer une couverture adéquate de la phase d'autorisation,
d'accréditation et de reconnaissance des établissements, de la phase de
suivi et de contrôle, ainsi que de la phase d’identification des anomalies,
de mise en œuvre des actions correctives et coercitives et d’application des
sanctions prévues à l’encontre des contrevenants.
Ainsi, il a été constaté que les délais prévus pour le traitement des
demandes d’autorisation sont souvent dépassés, et que les établissements
ne font pas l’objet d’une vérification à postériori par les services du
ministère chargé de l’enseignement supérieur afin de s’assurer de la
satisfaction des engagements pris, notamment en matière de disponibilité
des moyens matériels et pédagogiques. Il a également été relevé que le
contrôle administratif et pédagogique souffre d’une faible couverture des
établissements d’ESP, et que plusieurs domaines importants pour le
fonctionnement du secteur et la qualité de la formation ne sont pas couverts
par le contrôle. Cela limite le suivi du secteur par les services du ministère
et la détection des insuffisances de manière appropriée.
Par ailleurs, le ministère de tutelle ne prend pas, en temps opportun, des
dispositions à même d’appliquer les mesures coercitives et correctives
nécessaires, qui visent à corriger les insuffisances et les infractions relevées
lors des contrôles. Cette situation devrait permettre de limiter les
infractions et de favoriser la diffusion des bonnes pratiques dans le secteur.
Au vu de ce qui précède, et eu égard aux insuffisances structurelles que
connaît le système actuel de contrôle et de régulation de l’ESP, impactant
négativement son efficacité et partant sa contribution au développement du
secteur, la Cour des comptes a recommandé au Chef du gouvernement
de réviser le cadre juridique et institutionnel dudit système en conformité
avec les bonnes pratiques internationales, et ce dans l’optique de converger
vers une instance de régulation et de contrôle indépendante.


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              73
     La Cour a également recommandé au ministère de l’enseignement
     supérieur, de la recherche scientifique et de l’innovation d’élaborer une
     vision claire et une stratégie formalisée pour le développement du secteur
     de l’ESP, de développer et renforcer la coordination des activités des
     différents acteurs et intervenants en matière d’évaluation et de contrôle,
     ainsi que d’établir un cadre qui régit le partenariat public-privé. De plus, la
     Cour a recommandé au ministère de réviser le régime d’autorisation, de
     reconnaissance des EESP, d’accréditation des filières par l’État et les
     mécanismes de contrôle administratif et pédagogique, ainsi que de veiller
     à la mise en œuvre effective, le cas échéant, des mesures coercitives
     prévues par les textes réglementaires en vigueur.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
74                    - Principaux axes -
                Secteurs productifs, des
         infrastructures et de l’environnement


                            Villes nouvelles :
       Des opérations d’urbanisme qui manquent de cadrage
        stratégique, juridique et institutionnel efficace et qui
                 nécessitent une large mise à niveau

Le lancement de la création des villes nouvelles de Tamansourt, Tamesna,
Lakhyayta et Chrafate, à partir de 2004, témoignait d’un acte volontariste
des pouvoirs publics, afin de créer une nouvelle dynamique territoriale et
faire face aux enjeux de la croissance démographique et spatiale.
Concernant la planification et la conception des villes nouvelles, la
Cour a relevé que ces dernières ont été créées sans concordance avec les
documents d’aménagement du territoire et d’urbanisme. En effet, l’idée de
créer de nouvelles entités urbaines n’a pas été recommandée par les
orientations du Schéma national d’aménagement du territoire de 2002. De
même, les Schémas directeurs d’aménagement urbain élaborés avant le
lancement des villes nouvelles ne comprenaient pas l’ensemble desdites
villes.
Ainsi, la conception de ces villes a été dictée, principalement, par une
logique basée sur la disponibilité du foncier. A défaut d’un cadre juridique
les encadrant, elles ont été assimilées à des lotissements, et ce, malgré la
différence des concepts et des échelles entre lotissement et ville et la
complexité d’une telle forme urbaine aussi bien sur le plan démographique
que socio-économique.
Dans ce cadre, il convient de noter, également, l’absence d’un cadre
stratégique formalisé guidant la création des villes nouvelles, indiquant des
objectifs chiffrés appuyés d’indicateurs de performance, des budgets
alloués et d’un calendrier de réalisation réaliste. Dans ce sens, le Conseil
national de l’habitat avait insisté, en 2004, sur l'importance de mener des
études socio-économiques visant le renforcement et la mise à niveau du
système urbain aux niveaux national et régional. Toutefois, les projets des
villes nouvelles ont été lancés en l’absence des études d’opportunité et de
positionnement permettant de s’assurer de leur viabilité socio-économique.
De plus, l’offre massive en logements au niveau des villes nouvelles, qui
est le résultat d’un investissement considérable de l’État en infrastructure
et en équipement, a été impacté par l’ouverture d’autres zones à


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              75
     l’urbanisation autour de ces villes, notamment à travers les pratiques
     dérogatoires. En effet, les projets immobiliers construits dans ces zones ont
     imposé une concurrence réelle à l’offre de ces villes, sachant que les
     lotissements concernés bénéficient des équipements et des infrastructures
     desdites villes.
     Par ailleurs, le portage unilatéral des villes nouvelles par le département
     chargé de l’Habitat ne concorde pas avec le caractère multisectoriel et la
     multiplicité des acteurs intervenant dans les villes nouvelles. Ceci ne
     permet pas d’avoir une assurance raisonnable sur la convergence des
     visions de tous les acteurs. En outre, l’absence d’un schéma de
     gouvernance dédié aux villes nouvelles au niveau central et local,
     regroupant tous les acteurs, est de nature à compromettre la synergie entre
     les départements ministériels impliqués et la cohérence de leurs visions
     stratégiques sur les modalités de production et de gestion de ces créations
     urbaines.
     S’agissant du financement et de la gestion des villes nouvelles, ces
     dernières ont été initiées en l’absence d’un plan de financement en
     adéquation avec le volume des investissements requis. La revue des modes
     de réalisation des quatre villes fait ressortir l’absence d’un schéma
     convenable de financement de réalisation des équipements. Dans ce cadre,
     il convient de signaler que le financement de la réalisation des quatre villes
     nouvelles repose principalement sur le partenariat avec le secteur privé.
     Toutefois, il a été relevé, dans certains cas, des difficultés dans l’exécution
     des conventions avec les promoteurs partenaires. Ainsi, à fin 2023, sur 88
     conventions de partenariat avec les promoteurs privés au niveau des villes
     nouvelles, 52% des contrats sont résiliés ou en cours de résiliation. Cette
     situation a conduit à une croissance déséquilibrée de ces villes, caractérisée
     par un développement inégal du tissu urbain.
     En outre, la faible appropriation des projets des villes nouvelles par les
     communes (à caractère rural) auxquelles elles appartiennent a généré
     plusieurs problèmes en matière de gestion. En effet, ces projets n’ont pas
     été accompagnés par les moyens nécessaires permettant aux communes
     concernées d’assumer pleinement leurs nouvelles fonctions de gestion des
     villes nouvelles (collecte des déchets, nettoiement, maintenance, entretien
     des espaces verts, éclairage public, etc.). Il convient de noter que le
     Holding Al Omrane a supporté, jusqu’à fin 2023, un montant cumulé
     d’environ 305 MDH pour la gestion des différents services de base dans
     lesdites villes.
     Pour ce qui est des réalisations et des perspectives de développement,
     la Cour a relevé qu’à fin 2023, la population des quatre villes nouvelles,
     précitées, a atteint 169.036 habitants sur un objectif global d’un million


        Rapport annuel de la Cour des comptes au titre de 2023-2024
76                    - Principaux axes -
d’habitants, soit un taux ne dépassant pas les 17% de l’objectif initial. Le
nombre total des unités réalisées est de 71.486 unités, soit 20% de l’objectif
initial fixé à 350.000 unités de logement. L’investissement global réalisé
au niveau de ces villes est de l’ordre de 24,4 MMDH, soit 58% de
l’investissement global prévu qui est de l’ordre de 42,2 MMDH. La valeur
du stock total non écoulé détenu par le Holding Al Omrane au niveau
desdites villes est de l’ordre de 5,9 MMDH.
Par ailleurs, sur un nombre total d’équipements prévus (publics et privés)
de 659 équipements, 169 sont construits, soit un taux de réalisation de 26%,
dont 150 sont fonctionnels, soit un taux de mise en fonction de 23%.
Il y a lieu de signaler qu’afin de rattraper les retards dans les équipements,
des conventions de partenariat et de financement relatives à la relance et la
mise en valeur des villes nouvelles Tamesna et Tamansourt ont été
conclues respectivement en 2013 et 2014. Au niveau de Tamansourt, le
montant global à mobiliser est de 1.357 MDH, le projet du campus
universitaire, qui tarde à se concrétiser, coûte à lui seul 1.100 MDH, soit
81 % du montant global. Au niveau de Tamesna, le montant global à
mobiliser est de 538 MDH. Le délai de réalisation du plan de relance a été
fixé à cinq ans (2013-2017). Toutefois, la plupart des projets demeurent
toujours en cours de réalisation.
Eu égard à ce qui précède, la Cour a recommandé au Chef du
gouvernement de rehausser le portage des actions de l’État en matière de
villes nouvelles à un niveau stratégique garantissant la convergence et la
coordination entre les différents acteurs en la matière, de mettre en place
un plan de redressement des villes nouvelles actuelles et d’inciter le
département de tutelle à accompagner les communes abritant les villes
nouvelles afin qu'elles puissent progressivement assurer la gestion des
services publics dans ces villes.
Elle a recommandé, également, au ministère de l'Aménagement du
territoire national, de l'urbanisme, de l'habitat et de la politique de la
ville de mettre en place un cadre juridique dédié aux villes nouvelles,
définissant notamment les modalités de conception, planification,
gouvernance, financement, gestion et de protection de leurs zones
périphériques de l’ouverture à l’urbanisation.
Elle a, enfin, recommandé au Holding Al Omrane de recentrer l’activité
des sociétés Al Omrane sur leur mission de base fixée par leurs textes de
création et encadrer le processus de partenariat avec le secteur privé en
définissant en amont les garanties nécessaires à la bonne exécution des
conventions.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              77
                            Les chambres professionnelles :
       Leur contribution effective au développement des secteurs
      concernées dépend de la revue de leur positionnement et de
                          leur mise à niveau

     Les chambres professionnelles jouent un rôle important dans la promotion
     et le développement de l'économie nationale, eu égard à leurs attributions
     en matière de représentation, de consultation et de développement.
     Toutefois, elles sont confrontées à un ensemble de difficultés, liées à
     l'exercice de ces attributions, notamment en ce qui concerne la
     représentation de tous les professionnels, la coordination avec les autres
     acteurs, l'amélioration de leur gouvernance et la diversification des
     services rendus aux ressortissants. En 2023, le budget global alloué aux
     chambres professionnelles s'est élevé à environ 1.005 MDH, et le nombre
     de leurs salariés a atteint 1.314 personnes.
     En ce qui concerne les attributions des chambres professionnelles, il a
     été constaté que parallèlement aux chambres, d’autres organismes publics
     interviennent également dans le domaine du développement économique
     et social notamment les ministères de tutelle, les différents établissements
     publics intervenant dans le secteur et les collectivités territoriales,
     entraînant, ainsi, un chevauchement au niveau de l’exercice de leurs
     attributions avec celles de ces chambres. Il convient de souligner, à ce
     sujet, l’absence de mécanismes de coordination et de convergence des
     actions des différents acteurs.
     Concernant la représentation au sein des chambres professionnelles,
     elle ne reflète pas suffisamment la diversité des domaines d'intervention de
     ces dernières, ni les spécificités économiques et sociales du tissu
     économique qu'elles représentent. Dans certains cas, la représentation
     n'inclut pas certains professionnels et secteurs ou certaines collectivités
     territoriales disposant de potentiels économiques ou industriels importants
     au niveau de la région. En outre, les chambres connaissent une insuffisance
     des données concernant leur ressortissants. Dans ce sens, il y a lieu de noter
     que le taux d’inscription de professionnels sur les listes électorales par
     rapport au nombre potentiel de ressortissants demeure faible.
     Pour ce qui est de la planification stratégique, la plupart des chambres
     d'agriculture, des pêches maritimes et d'artisanat n'ont pas mis en place des
     plans stratégiques, permettant d’orienter leur action, ce qui se répercute
     négativement sur l'accomplissement de leurs missions, leurs modes de
     gestion et sur la réalisation de leurs objectifs. A cet égard, il convient de
     souligner que les chambres de commerce, d'industrie et de services ont
     élaboré leurs plans stratégiques suite à la signature des conventions


        Rapport annuel de la Cour des comptes au titre de 2023-2024
78                    - Principaux axes -
relatives aux plans de développement de ces chambres entre le ministère
de tutelle et le ministère de l’économie et des finances en 2018. Cependant,
ces plans n'ont pas pris en compte les plans de développement faisant
l'objet des conventions susmentionnés.
En ce qui concernent la représentation des chambres au sein des
conseils d'administration des institutions partenaires, les chambres
professionnelles sont membres aux conseils d'administration de plusieurs
établissements publics relevant de leur ressort territorial. Toutefois, elles
ne participent pas à toutes les réunions de certains conseils d'administration
ou à toutes leurs sessions, et qu’elles n’ont pas développé une vision leur
permettant d’avoir une participation plus significative aux réunions de ces
conseils. De plus, le rôle de consultation et de proposition des chambres
professionnelles demeure limité, et ce en raison de plusieurs facteurs,
notamment le manque de ressources humaines disposant de compétences
techniques et juridiques requises. De même, l'implication et la contribution
des chambres professionnelles à l’élaboration des stratégies nationales et
locales de développement restent limitées.
Concernant les missions d’appui et de formation, certaines chambres de
commerce, d'industrie et de services ont procédé à la création des instituts
de formation professionnelle. Cependant, le recours à ce mécanisme
comporte certains risques liés aux conflits d'intérêts, en raison de
l'incompatibilité entre l'adhésion à la chambre et l'exercice de fonctions de
gestion au sein des associations précitées. S’agissant des chambres des
pêches maritimes, elles n’ont organisé qu’un nombre limité de formations
pour les professionnels, faute de ressources financières et humaines
spécialisées dans les domaines liés à la pêche et à l'aquaculture. Quant aux
chambres de l'artisanat, elles ne disposent pas d'une vision claire à moyen
terme définissant les thèmes et les domaines des formations, se contentant
d'intégrer des activités de formation de nature générale dans leurs plans
d'action annuels.
En ce qui concerne les services rendus aux adhérents, les chambres
professionnelles n'ont pas initié la numérisation de leurs services, ce qui
limite leur capacité à fournir des services répondant aux besoins de leurs
membres et à contribuer au développement de leur environnement. En
outre, la création de guichets de proximité dans les chambres de commerce,
d'industrie et de services, à travers des partenariats avec les institutions
concernées (Office marocain de la propriété industrielle et commerciale,
l’Agence marocaine pour la promotion de la petite et de la moyenne
entreprise…) n'a pas connu le succès escompté.
S’agissant de l’organisation administrative et financière, il a été
constaté que les chambres professionnelles dépendent, principalement, des


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              79
     subventions de l'Etat pour couvrir l’essentiel de leurs dépenses, faute de
     ressources propres suffisantes leur permettant d'exercer leurs compétences
     et de financer leurs projets. En outre, l'adoption et l'opérationnalisation des
     mécanismes de bonne gouvernance demeure limitée, et avec un des degrés
     différenciés d'une chambre à l'autre, ce qui se répercute négativement sur
     leur gestion et la réalisation de leurs objectifs.
     Au vu de ce qui précède, la Cour a recommandé au ministère de
     l'industrie et du commerce, au ministère de l'agriculture, de la pêche
     maritime, du développement rural et des eaux et forêts, au ministère
     du tourisme, de l’artisanat et de l'économie sociale et solidaire, chacun
     dans son domaine de compétence, de revoir le positionnement des
     chambres professionnelles dans leur écosystème territorial et de renforcer
     leur rôle dans le but de contribuer efficacement au développement des
     secteurs concernés et de promouvoir les investissements.
     Elle a préconisé, également, de renforcer la représentation au sein des
     instances des chambres professionnelles pour refléter la diversité et les
     spécificités des secteurs et des activités qu'elles représentent au niveau
     territorial ; et d’établir un contrat-programme entre l'État et les chambres
     d'agriculture, des pêches maritimes et d’artisanat.
     La Cour a recommandé, enfin, de mettre en place de mécanismes de
     partenariat et de coordination en ce qui concerne les attributions communes
     entre les chambres professionnelles et les autres acteurs concernés ; et le
     renforcement de la représentation des chambres au sein des conseils
     d'administration des institutions partenaires.


                                  L’économie sociale et solidaire :
            Un secteur stratégique nécessitant une révision du cadre
                juridique et le renforcement de sa gouvernance

     Le secteur de l’économie sociale et solidaire (ESS) constitue un levier
     important de développement économique et social de notre pays,
     regroupant, à fin 2022, un nombre de 53.856 coopératives et 63 mutuelles.
     La même année, les coopératives ont généré une valeur ajoutée d’environ
     21,3 MMDH, soit environ 2% du PIB. Bien que l'ESS dispose d'un fort
     potentiel de développement, et que des efforts importants aient été
     déployés pour sa promotion, des défis à relever persistent.
     Sur le plan juridique, le secteur de l’économie sociale et solidaire dispose
     d’un cadre juridique fragmenté et non unifié. Dans ce sens, il convient de



        Rapport annuel de la Cour des comptes au titre de 2023-2024
80                    - Principaux axes -
signaler que le ministère chargé de l’économie sociale et solidaire a élaboré
un projet de loi-cadre, mais il est toujours en cours d’adoption.
S’agissant de la planification stratégique, la stratégie nationale de
développement de l’ESS, couvrant la période 2010-2020, a porté
uniquement sur le secteur des coopératives, et n’a pas constitué une feuille
de route intégrant l’ensemble des composantes du secteur, comme les
associations et les mutuelles, et répondant à leurs problèmes et leurs
besoins. En outre, cette stratégie n’a pas été déclinée en plans d’actions
détaillés, définissant les projets et les actions à réaliser, le montage
budgétaire adopté, les responsabilités des acteurs concernés, ainsi que les
indicateurs permettant d’assurer des évaluations quantitatives et
qualitatives des mesures prévues. Dans ce cadre, le ministère de tutelle a
élaboré 16 plans de développement régionaux de l’économie sociale
(PDRES). Néanmoins, seulement deux de ces PDRES, ont fait l’objet de
contrats programmes relatifs à leur exécution, entre le ministère chargé de
l’économie sociale et les conseils régionaux.
Il convient de souligner, dans ce sens, que les départements ministériels
concernés (ministère du tourisme, de l’artisanat et de l’économie sociale et
solidaire, ministère de l’Intérieur, ministère de l’agriculture…) planifient,
de manière isolée, leurs interventions dans ce domaine, en l’absence de
synergie et de coordination entre eux. Cette situation a impacté l’efficacité
des actions des différents acteurs, compte tenu des spécificités sectorielles
et du caractère transversal du secteur.
En matière de gouvernance, il a été constaté l’absence d’une instance au
niveau national pour coordonner et suivre l’exécution des stratégies et
programmes concernant le secteur, qui est, surtout, caractérisé par la
multiplicité des acteurs (les organisations de l’ESS, les départements
ministériels, les établissements et entreprises publics et les régions). Cette
situation engendre des défis en termes de coordination entre les
intervenants et de cohérence de leurs actions, notamment en l’absence de
mécanismes de concertation entre eux.
Par ailleurs, il a été constaté l'absence d'un système d’information intégré
dédié au secteur de l'économie sociale et solidaire. En effet, la production
des informations sur le secteur est caractérisée par son éparpillement et par
sa non exhaustivité, eu égard à la multiplicité des sources de données
(départements ministériels concernés, organisations opérant dans le
secteur, régions), ce qui ne permet pas à ces données de refléter la réalité
du secteur et sa contribution à l'économie nationale.
Eu égard à ce qui précède, la Cour a recommandé au ministère du
tourisme, de l’artisanat et de l’économie sociale et solidaire, de mettre
en place un cadre juridique unifié et homogène pour l’ESS pour assurer


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              81
     son organisation et son développement; et d’adopter une stratégie nationale
     globale et intégrée, tenant compte les besoins des organisations opérant
     dans le secteur, en coordination avec les différentes parties prenantes, tout
     en mobilisant les moyens nécessaires au financement des projets.
     La Cour a recommandé, également au ministère, de renforcer le cadre
     institutionnel du secteur de l’ESS, tout en veillant à la mise en place
     d’instances de gouvernance efficaces, aux niveaux national et régional,
     afin de garantir l’adhésion de l’ensemble des acteurs concernés et d’assurer
     la coordination et le suivi des stratégies et des programmes adoptés; et de
     renforcer les mécanismes de veille et de suivi en mettant en place un
     système d’information intégré permettant d’avoir une vision globale de
     toutes les composantes du secteur et de suivre l’exécution des programmes
     publics en la matière.
     La Cour a recommandé, enfin, de mettre en place une plateforme
     intégrée englobant l’ensemble des intervenants dans le secteur de l’ESS et
     regroupant tous les programmes et initiatives de soutien et
     d’accompagnement ; et de renforcer la communication autour de ces
     programmes, afin de généraliser et faciliter l'accès des populations
     concernées.


           Actions nationales pour faire face au changement
                              climatique :
              Difficultés dans la mise en œuvre des stratégies et dans
                          l’atteinte des objectifs escomptés

     Le Maroc fait face à d’importants défis liés au Changement climatique
     (CC), qui se manifestent, principalement par une hausse significative des
     températures et une faiblesse et irrégularité des précipitations, provoquant
     une situation de stress hydrique chronique. Pour faire face à ces défis, notre
     pays s’est engagé à mettre en œuvre des actions d’atténuation pour réduire
     ses émissions de gaz à effet de serre, ainsi que des actions d’adaptation
     pour renforcer sa résilience.
     Dans ce sens, la version actualisée de la contribution déterminée au niveau
     national (CDN) de 2021 a porté l’objectif d’atténuation à 45,5% à l’horizon
     2030, dont un objectif inconditionnel de 18,3%. Ainsi, elle a prévu 61
     actions d’atténuation, pour un coût total de 38,8 milliards USD, dont 34
     actions inconditionnelles, estimées à 17,3 milliards USD à l’horizon 2030.
     Ladite CDN a également identifié des actions en matière d’adaptation dans




        Rapport annuel de la Cour des comptes au titre de 2023-2024
82                    - Principaux axes -
huit secteurs pour un coût estimé à près de 40 milliards USD à l’horizon
2030.
Cette mission d’évaluation, qui a concerné la période 2014 à 2023, a eu
pour objet d’examiner dans quelle mesure les actions prévues par les
stratégies et les plans établis par le département du développement durable
(DDD) permettraient d’atteindre les objectifs escomptés en termes de lutte
contre le CC.
Concernant le cadrage juridique et la gouvernance des actions
climatiques, il a été noté que le cadre juridique climatique en vigueur est
incomplet dans la mesure où il ne fixe pas des objectifs nationaux clairs, et
ne définit pas les rôles et les responsabilités des différentes parties
prenantes, aussi bien au niveau national qu’au niveau territorial. En outre,
l’instauration de la Commission nationale du changement climatique et de
la diversité biologique, en tant qu’organe de concertation et de
coordination pour la mise en œuvre de la politique nationale relative au
CC, a accusé un retard dépassant six ans. La Cour a relevé, également,
qu’en dépit de son institutionnalisation en 2020, elle ne remplit pas
pleinement ses missions en raison de son efficacité réduite due, entre
autres, à l’absence d’une définition claire et adéquate de sa composition,
de ses responsabilités, de ses pouvoirs et de ses moyens. En effet, le
nombre pléthorique des membres participants, supérieur parfois à 70, et
leur pouvoir restreint (certains organismes sont représentés par des cadres
ou des chefs de service) limitent l’efficacité de cette instance.
Quant aux mécanismes de suivi conçus par le DDD, ils sont multiples, mais
demeurent non interconnectés et non intégrés dans un système global de
collecte et de diffusion de l’information. De plus, ces systèmes ne sont pas
opérationnels, en raison de l’absence d’un plan de conduite de changement
pour accompagner la multitude des acteurs et des secteurs concernés. Pour
ce qui est des actions de communication du DDD relatives au CC, elles
restent ponctuelles et non coordonnées en l’absence d’une stratégie dédiée.
S’agissant des stratégies et plans relatifs aux actions climatiques, le
DDD a élaboré la politique du CC au Maroc de 2014, la Contribution
déterminée au niveau national (CDN) de 2016 et de celle actualisée de
2021, la stratégie nationale du DD de 2017, le plan climat national de 2019,
la stratégie de développement bas carbone de 2021 et le plan national
stratégique d’adaptation de 2022. Néanmoins, ces stratégies et plans n’ont
pas déterminé systématiquement, lors de leur conception, des indicateurs
cibles spécifiques, mesurables et temporellement définis. Quant aux bilans
des actions climatiques, ils restent vagues et ne permettent pas de constater
le degré de mise en œuvre des actions prévues, ainsi que les écarts




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              83
     enregistrés. Dans ce sens, la CDN a été actualisée en 2021 sans une
     évaluation des réalisations de sa première version de 2016.
     De surcroît, l’ensemble des stratégies et plans précités se sont limités à des
     orientations stratégiques et redondantes. Ces documents n’ont pas été
     déclinés en plans d’actions opérationnels avec des actions spécifiques
     adossées à des échéances et des budgets, tout en définissant les rôles et les
     responsabilités des différentes parties prenantes. De même, le DDD n’a pas
     procédé à une concertation préalable avec le ministère de l’Economie et
     des finances (MEF) en vue d’avoir une cohérence entre les actions
     proposées et les contraintes budgétaires, en particulier en ce qui concerne
     les mesures inconditionnelles.
     Pour leur part, les Plans climat territoriaux (PCT), élaborés par le DDD,
     n’ont pas permis d’apporter une valeur ajoutée notable en matière de lutte
     contre le CC, en raison notamment, de la non implication suffisante des
     principales parties prenantes au niveau territorial, notamment les
     collectivités territoriales et les établissements et les entreprises publics
     dans leur élaboration et leur suivi, de leur faible alignement avec les
     documents stratégiques régionaux et du caractère générique des actions
     proposées. Dans ce sens, bien que les caractéristiques climatiques des
     régions présentent des différences, certains PCT ont proposé quasiment les
     mêmes plans d’adaptation prioritaires.
     Pour ce qui est du financement des actions climatiques, le Maroc ne
     dispose pas d’une classification permettant d’identifier les investissements
     et les activités économiques qui respectent l’environnement, ce qui
     engendre des difficultés dans la mise en œuvre d’actions climatiques
     efficaces, et ne favorise pas la canalisation des capitaux vers les
     investissements éco-responsables.
     De plus, notre pays ne dispose pas d’un budget sensible au climat en bonne
     et due forme. En outre, l’estimation des besoins de financement n’est pas
     accompagnée de calendrier de mobilisation des financements prévus.
     Par ailleurs, l’information relative aux dépenses climatiques au niveau
     national demeure limitée, non actualisée, et non exhaustive.
     En outre, la contribution du secteur privé au financement climatique reste
     modeste. En effet, selon le panorama des financements climatiques au
     Maroc, seuls 23% du total des financements climatiques ont été mobilisés
     par le secteur privé sur la période 2011-2018.
     Pour sa part, le financement international demeure généralement faible,
     notamment en ce qui concerne les mesures d'adaptation. De même, il est
     caractérisé par l'absence d'un système centralisé de collecte des données.



        Rapport annuel de la Cour des comptes au titre de 2023-2024
84                    - Principaux axes -
En effet, selon le « Adaptation Gap Report » publié par le Programme des
Nations unies pour l'environnement en 2023, le financement de l'adaptation
mobilisé par le Maroc entre 2017 et 2021 n'a pas dépassé 2,1 milliards
USD, ce qui reste limité par rapport aux besoins déclarés d'environ 35
milliards USD selon la CDN de 2016.
Au vu de à ce qui précède, la Cour a recommandé au Chef du
gouvernement, de placer sous sa tutelle la Commission nationale du
changement climatique, eu égard à son caractère stratégique.
Elle a également recommandé au département du développement
durable de mettre en place un cadre juridique instaurant l’obligation des
actions d’atténuation et d’adaptation aux effets du CC, ainsi que des
modalités de coordination, et de responsabilisation des parties prenantes
clés, et d’actualiser les stratégies et les plans nationaux d’atténuation et
d’adaptation en définissant, notamment, des objectifs spécifiques,
mesurables, atteignables et temporels ainsi que des modalités de suivi et
d’évaluation de leur mise en œuvre.
Elle lui a aussi recommandé de mettre en place des plans d’adaptation
territoriaux spécifiques et adaptés à chaque territoire avec des objectifs
clairement définis ainsi que les moyens mis à leur disposition pour les
atteindre et les modalités de suivi et d’évaluation de leur mise en œuvre, et
instaurer un système intégré de suivi et d’évaluation des actions
d’atténuation et d’adaptation, en veillant à l’interconnexion des sources de
données des principales parties prenantes, ainsi qu’à la définition de leurs
responsabilités dans le processus de collecte des données.
De même, la Cour a recommandé au ministère de l’Economie et des
finances de mettre en place des mécanismes permettant une meilleure
identification, estimation des besoins et suivi des investissements
climatiques, et de renforcer le rôle du secteur privé dans le financement
climatique par la mise en place d’incitations adéquates, et l’amélioration
du cadre du partenariat public privé.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              85
           L’agriculture face aux changements climatiques :
         Défis majeurs nécessitant une approche globale à même de
         garantir la cohérence entre les exigences du développement
              durable et les mesures d’adaptation aux effets du
                           changement climatique

     Le secteur de l’agriculture est confronté à d’importants défis liés aux
     changements climatiques, se manifestant par la rareté des précipitations et
     leur irrégularité, par l’augmentation de la température, ainsi que par
     d’autres évènements extrêmes associés au climat. Ce secteur est, ainsi,
     considéré comme l'un des plus touchés par ces phénomènes, qui entraînent
     notamment une faiblesse des récoltes agricoles à cause de la réduction des
     surfaces cultivées et de la baisse des rendements.
     Ce secteur est également au cœur d'un double défi : assurer la sécurité
     alimentaire par l'augmentation de la production et l'amélioration de
     l'efficacité de l'utilisation des ressources pour répondre aux besoins d'une
     population dont le nombre ne cesse de croître, et la nécessité de préserver
     les ressources naturelles et d'en assurer leur durabilité.
     La mission thématique sur l’agriculture face aux changements climatiques
     a examiné la prise en compte de ces changements dans les politiques et
     stratégies agricoles et a apprécié l’efficacité des programmes d’atténuation
     et d’adaptation mis en œuvre dans le cadre de la contribution déterminée
     au niveau national du département de l’agriculture, qui est considéré
     comme le deuxième émetteur des gaz à effet de serre à l’échelle nationale
     avec une part d’environ 22,8% en 2018.
     Concernant le cadre juridique et stratégique relatif à la lutte contre
     les effets des changements climatiques dans le secteur agricole, des
     efforts importants ont été déployés pour le renforcement du cadrage
     juridique du développement durable, en général, au cours des dernières
     décennies. Néanmoins, ce cadre reste incomplet, notamment au vu du
     retard pris dans l'adoption de certains textes d’application, à l’instar du
     texte d’application, de la loi n°49.17 relative à l'évaluation
     environnementale, portant sur la procédure d'élaboration, d'examen et
     d’exécution de l'évaluation environnementale stratégique, ainsi que les
     textes d'application de la loi n° 01.06 relative au développement durable
     des palmeraies et portant protection du palmier dattier. En outre, il a été
     constaté l’absence d’un corpus juridique spécial visant à protéger les sols
     contre toutes les formes de dégradation. Dans ce sens, il convient de
     signaler que le projet de loi n°42.10 sur la protection des sols n'est pas
     toujours adopté, malgré la pression croissante sur ces ressources en raison
     des activités socio-économiques.


        Rapport annuel de la Cour des comptes au titre de 2023-2024
86                    - Principaux axes -
La Cour a relevé, également, des insuffisances au niveau de la coordination
et de la synergie entre les orientations stratégiques liées aux changements
climatiques et les stratégies agricoles, dans la mesure où ces dernières ne
sont pas alignées sur les objectifs nationaux de lutte contre les changements
climatiques. Dans ce sens, l’atteinte des objectifs de la stratégie «
Génération Green » nécessite la prise en compte d’un ensemble de
considérations comme éléments clés dans la conception des projets et
mesures agricoles, notamment les spécificités géographiques des
différentes régions, la sensibilité des territoires et des écosystèmes
particuliers aux effets des changements climatiques, la vocation des terres,
la rationalisation de l'exploitation des ressources hydriques et leur
protection. Il y a lieu, également de souligner dans ce contexte, la nécessité
de mise en place de mécanismes permettant de suivre et d'évaluer, de
manière permanente et continue, le degré d'exposition aux phénomènes liés
aux changements climatiques et leurs effets sur le secteur, afin de disposer
de données permettant d'élaborer des stratégies et plans d'action
d'adaptation adéquats.
S’agissant de la recherche scientifique, il est nécessaire d'exploiter de
manière optimale les résultats des recherches qui abordent les
problématiques liées aux changements climatiques dans le domaine
agricole, en termes d'atténuation ou d'adaptation, et d'œuvrer à leur mise
en œuvre en renforçant la communication entre les institutions de
recherche, et en favorisant la diffusion des connaissances et leur
vulgarisation auprès des agriculteurs. Dans ce cadre, il convient de
souligner que le système de recherche agronomique souffre d’insuffisances
liées à la faiblesse de la coordination et de la coopération dans le domaine
de la recherche agricole au niveau national, et l’absence d'un système de
gestion de la connaissance reliant toutes les institutions de recherche
scientifique agricole et permettant l'échange des ressources et le partage
des résultats afin d’améliorer l'efficience et l'efficacité de la recherche
scientifique dans le domaine agricole.
Pour ce qui est des mesures d’atténuation des émissions de gaz à effet
de serre, l’examen de l’inventaire des émissions du secteur agricole, qui
ont atteint 20.729 Gigagramme en 2018, a révélé que les mesures
d'atténuation mises en œuvre n'ont pas réussi à limiter l'évolution de ces
émissions et les ramener aux niveaux escomptés. En effet, en l’absence
d’une approche systémique prenant en considération les différentes
composantes environnementales au niveau des actions exécutées et tenant
compte des principales sources d’émissions des gaz à effet de serre, ces
mesures basées, principalement, sur les plantations arboricoles n’ont pas
été suffisantes pour réduire les émissions dues aux changements
d’affectation des terres. Il convient de signaler, dans ce sens, que le secteur


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              87
     agricole est le premier émetteur de méthane (CH4) avec une part de 62,4%,
     et le principal émetteur de protoxyde d’azote (N2O) avec une part de 92,4%
     du total des émissions.
     En matière d’adaptation aux effets des changements climatiques, dans
     le contexte de la situation du stress hydrique que connait le pays, il est
     devenu crucial d’assurer la rationalisation et la pérennisation des
     ressources en eau allouées à l'irrigation, en tenant compte des risques des
     changements climatiques au niveau des projets d'extension et de
     modernisation des systèmes d'irrigation. Dans ce cadre, la contribution
     déterminée au niveau national a retenu des programmes importants
     d'adaptation du secteur agricole tels que le programme d'assurance agricole
     et les programmes de gestion de l'eau d'irrigation tels que le programme
     national d'économie de l'eau d'irrigation (PNEEI), dont les superficies
     aménagées ont atteint 794.400 hectares, et le programme d'extension de
     l'irrigation (PEI) avec une superficie réalisée de 39.020 hectares.
     Néanmoins, ces programmes nécessitent une évaluation périodique afin
     d’alerter sur les impacts induits par les restrictions de fourniture d’eau aux
     périmètres irrigués sur la productivité, le revenu des agriculteurs et
     l’emploi agricole, ainsi que la révision du PEI en fixant des objectifs qui
     tiennent compte des ressources en eau mobilisables.
     En ce qui concerne l'assurance multirisques climatiques, le taux
     d'adhésion des agriculteurs à cette assurance reste faible malgré
     l'augmentation enregistrée au cours de la période 2012-2023, puisqu'il est
     passé de 7% lors de la campagne agricole 2011-2012 à 24% pendant la
     campagne 2022-2023, soit 1,2 million d’hectare. Dans ce sens, face à un
     contexte marqué par une augmentation de la sinistralité des cultures
     agricoles, suite à la succession des années de sécheresse et de phénomènes
     climatiques extrêmes, les risques liés à la pérennisation des produits
     d’assurance agricole sont de plus en plus importants et nécessitent la
     conception de nouveaux modes de financement innovants.
     Eu égard à ce qui précède, la Cour a recommandé au ministère de
     l'agriculture, de la pêche maritime, du développement rural et des
     eaux et forêts de veiller à l’élaboration et la mise en œuvre des plans
     d’action thématiques et des plans agricoles régionaux prévus par la
     stratégie Génération Green, tout en procédant aux ajustements nécessaires
     afin d’assurer leur convergence et leur synergie avec les stratégies
     nationales relatives aux changements climatiques ; et d’adopter, au niveau
     du secteur agricole, une approche systémique permettant la cohérence et
     la complémentarité entre les objectifs du développement durable et les
     mesures retenues d’atténuation des GES et d’adaptation aux effets des
     changements climatiques.



        Rapport annuel de la Cour des comptes au titre de 2023-2024
88                    - Principaux axes -
Elle a recommandé, également, d’accélérer la réalisation des projets
d’irrigation par les eaux non conventionnelles, grâce notamment au
dessalement de l’eau de mer, et encourager l’utilisation des énergies
renouvelables dans le domaine de l’irrigation, tout en veillant à un contrôle
de proximité de l’usage de l’eau d’irrigation afin d’assurer sa
rationalisation.
Elle a, enfin, recommandé de mettre en place une vision intégrée de la
recherche scientifique relative aux thématiques traitant les changements
climatiques dans l’agriculture, et la traduire en contrats programmes entre
l’Etat et les différentes institutions de recherche agronomique.




                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              89
                    Développement territorial et gestion
                     des services publics territoriaux


                            Approvisionnement en eau potable :
        Assurer un approvisionnement suffisant et durable, nécessite
        l’accélération de l’exécution des grands projets structurants
                  et la rationalisation de la consommation

     Notre pays a mis en œuvre de nombreux projets pour assurer
     l'approvisionnement de la population en eau potable, notamment dans le
     cadre du programme national intégré d'approvisionnement des zones
     rurales en eau potable (1995), de la stratégie nationale de l'eau 2009-2030,
     et du programme national pour l’approvisionnement en eau potable et
     l'irrigation 2020-2027. Parmi les projets les plus importants réalisés jusqu'à
     la fin de l'année 2022, on compte la construction de 44 grands barrages et
     15 stations de dessalement, le raccordement des bassins du Sebou et du
     Bouregreg, et le relèvement du taux d'accès de la population à l'eau potable
     à plus de 98%. Malgré ces efforts, notre pays continue à faire face à des
     défis majeurs, liés à la pénurie sévère et croissante de ressources en eau, à
     cause de la succession des années de sécheresse, et de l’augmentation de
     la demande résultant de la croissance démographique.
     A ce propos, les Cours régionales des comptes (CRC), en coordination
     avec la Chambre compétente à la Cour des comptes, ont réalisé une mission
     thématique portant sur l’état actuel de l’approvisionnement en eau potable
     et l’évaluation du système y afférent.
     Concernant le cadre juridique et institutionnel relatif à l'eau, et jusqu’à
     mars 2024, seuls neuf (9) textes réglementaires ont été publiés, et ne
     couvrant pas tous les aspects auxquels a renvoyé le législateur dans la loi
     n°36.15 relative à l’eau (70 renvois), en particulier, ceux abordés pour la
     première fois, et portant surtout sur les modalités et conditions de
     conclusion des contrats de gestion participative, d’établissement et révision
     des plans de gestion des pénuries d'eau, et d’élaboration du système
     d’information relatif à l’eau. Ladite loi ne traite pas non plus, certains
     aspects essentiels tels que la déminéralisation des eaux saumâtres, l'audit
     des réseaux de distribution d'eau potable, et l’encadrement de
     l’intervention des associations dans la production et la distribution de l’eau
     potable, notamment en milieu rural.




        Rapport annuel de la Cour des comptes au titre de 2023-2024
90                    - Principaux axes -
Également, les commissions préfectorales et provinciales de l'eau, n'ont
pas été créées dans 16 préfectures et provinces, ou créées tardivement dans
une préfecture et 5 provinces, ou bien n’ont pas été activées dans 7
provinces. De plus, les ressources humaines et matérielles allouées à la
police de l’eau s’avèrent assez faibles. En effet, celle-ci ne disposait, en
2022, que de 144 agents répartis entre le ministère de l’équipement et de
l’eau (86 agents), et les agences des bassins hydrauliques (58 agents) ; ce
qui ne favorise pas la réalisation d’enquêtes sur le terrain, de façon
continue et dans tout le périmètre d’intervention de la police de l’eau.
Au niveau de la planification stratégique et des outils de
programmation, l'élaboration de nombre de conventions de partenariat
pour l'approvisionnement en eau potable, soulève des lacunes tenant
surtout au manque de convergence, à la non-précision de la nature et de la
consistance des projets, ainsi qu’à la non-détermination de la
programmation et des lieux de leur réalisation. Par ailleurs, l’intervention
de plusieurs parties dans la réalisation des projets liés à
l’approvisionnement en eau potable, à la gestion et l’exploitation des
ouvrages hydrauliques réalisés, autant qu’au contrôle de la qualité de l’eau
distribuée, et en l’absence de mécanismes de coordination et de garantie de
la convergence, pourrait affecter négativement l’efficacité des actions
publiques, en termes de satisfaction des besoins de manière intégrée et
globale, et rendant ainsi difficile l’évaluation des actions entreprises et la
détermination des responsabilités.
S’agissant de l’offre et de la demande en eau potable, Il a été relevé que
les ressources hydriques mobilisées restent insuffisantes pour répondre aux
besoins nationaux. En effet, plus de 50% des ressources en eau de surface
sont concentrées dans les deux bassins du Loukkos et Sebou, qui couvrent
7% de la superficie du Royaume, et enregistrent un excédent annuel de
1,23 milliard de m3 ; alors que les huit autres bassins, connaissent un déficit
annuel total de 3,03 milliards de m3 ; et il est prévu que les besoins
nationaux en eau augmentent de 44% à l’horizon 2050. De plus, l’écart
enregistré sur la période 2018-2022, entre les cadences d’accroissement de
la demande (20%) et de l’offre (17%), pose de sérieux défis liés à
l’approvisionnement en eau potable, surtout qu’il est fait recours à cet
égard, pour 99% aux ressources conventionnelles (68% eau de surface et
31% eau souterraine), et pour seulement 1% aux ressources non-
conventionnelles (eaux saumâtres ou de mer dessalées).
Durant la période 2017-2022, les ressources en eau souterraine ont servi à
satisfaire, plus de la moitié des besoins en eau potable dans sept régions ;
ces ressources subissent d’ailleurs une surexploitation au niveau de tous
les bassins, dès lors que leur volume mobilisé dépassant de plus d'un
milliard (01) de m³ celui exploitable. Cette situation est due à la non-mise


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              91
     en action des mécanismes de protection et de préservation desdites
     ressources en eau, autant qu’à l’insuffisance des efforts de leur exploration.
     Dans le même sens, des retards ont été constatés dans l'élaboration et
     l’application des contrats de gestion participative pour les nappes, qui
     constituent un des mécanismes les plus importants prévus par la loi sur
     l’eau, afin d’assurer une utilisation durable de ces ressources hydriques
     ainsi que leur préservation ; seulement 5 contrats ont été conclus sur les 36
     prévus.
     Par ailleurs, en se basant sur les données de 2021 fournies par les parties
     concernées (l’ONEE, les régies autonomes et les sociétés de gestion
     déléguée), et en considérant des taux de rendement national des réseaux de
     distribution et de production qui s’établissent, respectivement, à 76% et
     80%, les réseaux d’adduction et de distribution connaissent d'importantes
     pertes d’eau, estimées à 653 millions de m3 par an, dont 320 millions de
     m³ d’eau potable. Les capacités de stockage des systèmes de distribution
     de l’eau potable, gérés par lesdits organismes, ont enregistré une
     amélioration notoire au cours de la période 2017-2022, s’élevant à 12%.
     Néanmoins, l’autonomie de stockage varie parfois considérablement, selon
     les différents systèmes de distribution, avec des valeurs allant de 2 à 61
     heures dans la région de l’Oriental, de 4 à 24 heures à la région de
     Casablanca-Settat, de 3 à 53 heures à la région de Drâa-Tafilalet, et de 4 à
     36 heures à la région de Tanger-Tétouan-Al Hoceima.
     En ce qui concerne les mesures prises pour assurer
     l’approvisionnement durable en eau potable, il a été constaté un retard
     dans la réalisation des projets de raccordement des bassins versants, prévus
     à la stratégie nationale de l'eau 2009-2030, tel que le projet portant sur le
     transfert de l'excédent d'eau du bassin du Sebou, vers le barrage de Sidi
     Mohamed Ben Abdallah dans le bassin du Bouregreg, et le raccordement
     de celui-ci au barrage d’Al-Massira dans le bassin d'Oum Errabia, visant à
     renforcer et sécuriser l'approvisionnement en eau potable du grand
     Marrakech.
     De même, les travaux de construction de six (6) barrages accusent un retard
     par rapport aux prévisions de la stratégie susvisée ; il s’agit des barrages
     de Sidi Abbou dans la province de Taounate (8 ans), Kheng Grou dans la
     province de Figuig (7 ans), Taghzirt dans la province de Béni Mellal et
     Boulaouane dans la province de Chichaoua (5 ans), Beni Azimane dans la
     province de Driouch (4 ans), et Ait Ziat dans la province d’Al Haouz (1
     an).
     En outre, il est relevé le non-respect du calendrier prévu pour la réalisation
     du projet relatif à la construction de la station de dessalement à Casablanca,
     qui devait être lancé en 2010, mais dont l'appel à manifestation d'intérêt n'a


        Rapport annuel de la Cour des comptes au titre de 2023-2024
92                    - Principaux axes -
été lancé qu'en mars 2022 ; en plus de la non-réalisation du projet de
dessalement à Saïdia, qui devait être lancé en 2015 ; en revanche, il a été
programmé le lancement en 2022, d’une étude de faisabilité d’un projet de
dessalement de l’eau de mer à Nador.
De plus, il a été relevé que l’exécution de 78 projets portant sur la
production et la distribution de l’eau potable, dont le coût global s’élève
jusqu’au juillet 2022 à 3,9 MMDH, connaît des difficultés liées
principalement aux conséquences de la pandémie COVID-19, et au
renchérissement des prix des matières premières d’une part ; et aux
dommages ayant affecté ces projets à cause des travaux de construction de
routes et de pistes adjacentes, sans prendre les précautions nécessaires,
d’autre part.
Eu égard à ce qui précède, la Cour des comptes a recommandé au
ministère de l'équipement et de l'eau d'élaborer des dispositions
législatives et réglementaires cadrant de façon précise les aspects relatifs à
l'audit des réseaux d’adduction et de distribution de l’eau, au dessalement
de l'eau de mer, à la déminéralisation des eaux saumâtres, à l'utilisation des
eaux usées traitées, ainsi qu’à l'intervention des associations dans
l'approvisionnement en eau potable. Elle a également recommandé
d’établir et de mettre en œuvre les plans de gestion de la pénurie d'eau au
niveau des régions et zones concernées, en veillant à donner la priorité à
l'approvisionnement de la population en eau potable, et en affectant le reste
des réserves disponibles en eau à la mise au point des programmes
d'irrigation, en coordination avec le département chargé de l’agriculture ;
et d’accélérer la cadence d’exécution des projets programmés pour
l'approvisionnement en eau potable, en particulier les grands projets
structurants, tout en assurant la cohérence et la convergence des
interventions des différents acteurs, et en activant les mécanismes
d'évaluation et de suivi des projets.
De plus, la Cour a préconisé la promotion de la recherche scientifique et
technologique dans le domaine de l’eau, à travers l’établissement de
partenariats entre les différents départements gouvernementaux concernés
d’une part, et les universités et les écoles supérieures d’autre part ; en vue
de développer les techniques utilisées pour réduire le coût de production
de l’eau non-conventionnelle, notamment le dessalement de l’eau de mer,
tout en tenant compte de la dimension environnementale.
La Cour a recommandé également au ministère de l’intérieur de
finaliser l’élaboration et la publication des textes d'application de la loi
n°36.15 relative à l'eau ; d'activer les commissions préfectorales et
provinciales de l'eau pour coordonner et suivre les actions prises pour gérer
la pénurie de l’eau ; de réaliser des audits réguliers sur les réseaux de


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              93
     distribution de l'eau potable, et d’entreprendre les mesures nécessaires pour
     améliorer leur rendement, et ce en surveillant, de manière proactive, les
     fuites d’eau et les branchements illégaux auxdits réseaux.


                 Parc de véhicules et d'engins des collectivités
                    territoriales et de leurs groupements:
             Réforme indispensable pour une meilleure gouvernance

     Les collectivités territoriales et leurs groupements disposent d’un parc
     important de véhicules, d'engins et de motocycles de différentes catégories,
     représentant un total de 48.495 unités en 2023. Ce parc représente l’un des
     piliers essentiels des fonctions supports, indispensables pour assurer un
     fonctionnement efficace, continu et durable des services publics. Il permet
     de répondre aux attentes des citoyens tout en garantissant une gestion
     conforme aux principes d’économie, d’efficience et d’efficacité.
     Dans ce cadre, le nombre de véhicules et d’engins des collectivités
     territoriales et de leurs groupements a connu une évolution notable entre
     2016 et 2023, passant de 24.545 unités en 2016 à 36.000 unités en 2023,
     soit une augmentation de 46%, avec un taux de croissance annuel moyen
     de 6%.
     Pour les dépenses de fonctionnement liées au parc de véhicules et d'engins
     durant la période 2016-2022, elles ont atteint environ 6,2 MMDH. Les
     dépenses en carburant et en lubrifiants ont constitué le principal poste de
     dépenses, avec un montant de 3,2 MMDH, soit 52 % des dépenses totales
     sur cette même période. Ces dépenses ont également connu une
     augmentation notable entre 2016 et 2022, passant de 786 MDH en 2016 à
     1.044 MDH en 2022, soit une hausse d’environ 33%, avec un taux de
     croissance annuel moyen de 4,8%.
     Quant aux dépenses d'équipement liées au parc de véhicules et d'engins,
     elles ont suivi une évolution fluctuante sur la période 2016-2022. En effet,
     leur moyenne entre 2016 et 2019 s'élevait à 885 MDH, avant de connaître
     une baisse significative en 2020 et 2021, avec une moyenne de 490 MDH,
     en raison des répercussions de la crise sanitaire liée à la COVID-19. Ces
     dépenses ont ensuite repris leur hausse en 2022, atteignant 546 MDH, soit
     une augmentation de 9% par rapport à 2021.
     S'agissant du cadre juridique, à la différence des véhicules et engins
     utilisés par les départements ministériels, régis par un ensemble de décrets,
     circulaires et notes, la gestion de ceux des collectivités territoriales n’est
     pas encadrée par un dispositif juridique intégré et exhaustif. Un tel


        Rapport annuel de la Cour des comptes au titre de 2023-2024
94                    - Principaux axes -
dispositif permettrait de définir les composantes de ce parc, ainsi que les
modalités de leur exploitation, tout en précisant, de manière exclusive, les
personnes pouvant bénéficier de son usage individuel. Cette situation,
associée à l’absence de directives et de normes professionnelles et
organisationnelles, a donné lieu à une utilisation du parc qui ne tient pas
compte des principes d’économie, d'efficacité et de performance, ainsi que
des rôles fonctionnels des différents composants du parc lors de leur
affectation et utilisation.
Sur le plan institutionnel, l’intervention des différents acteurs
directement ou indirectement liés à la gestion de ce parc (Collectivités
territoriales, Ministère de l’Intérieur, Agence nationale de la sécurité
routière, Société nationale des transports et de la logistique) obéit à une
logique verticale. À cet égard, il a été relevé un manque de coordination et
de convergence de visions quant aux moyens à même d’instaurer une
gestion intégrée et globale, qui vise l’économie et l’efficacité dans la
gestion de l’ensemble des opérations relatives au parc, et qui favoriserait
également la consécration des bonnes pratiques tout au long du cycle de
vie du parc.
Quant au rôle du parc de véhicules et d’engins dans le soutien à
l’exercice des attributions des collectivités territoriales, il a été observé
un manque de prise en compte des rôles fonctionnels du parc lors du
processus d’acquisition. En effet, les acquisitions effectuées entre 2016 et
2023 ont concerné à 77 % des véhicules légers classés CI (conduite
intérieure) et des véhicules utilitaires de moins de 3,5 tonnes, destinés
principalement à des usages individuels. En revanche, seuls 23% des
acquisitions ont concerné des engins, des tracteurs et des véhicules
utilitaires de plus de 3,5 tonnes, directement liés à l'exercice des
attributions des collectivités territoriales. En conséquence, les
composantes du parc ne sont pas utilisées principalement comme un
moyen de soutien à l’exercice des fonctions et compétences essentielles
dévolues aux collectivités territoriales. Elles sont souvent affectées à des
usages individuels, qui ne sont pas nécessairement liés à l’utilisation de ces
véhicules et engins à des fins administratives.
S'agissant de la gestion opérationnelle du parc, plusieurs insuffisances
ont été relevées, concernant l'identification des besoins, l'acquisition,
l’exploitation et l’utilisation ainsi que la mise en réforme. Ces
insuffisances se manifestent principalement par ce qui suit :
    •   Pour la définition des besoins et la politique d'acquisition, il a
        été principalement enregistré que la majorité des collectivités
        territoriales ne dispose pas d’un plan annuel ou pluriannuel
        d'acquisition, et que les prévisions budgétaires ne se basent pas sur


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              95
                 les besoins réels en véhicules et engins ainsi que sur leurs
                 caractéristiques. De plus, la plupart des acquisitions sont réalisées
                 selon des procédures qui n'exploitent pas pleinement les avantages
                 de la concurrence pour réduire les coûts. Par ailleurs, un recours
                 croissant à la location longue durée (LLD), sans encadrement
                 approprié, a été observé. Cette pratique se fait sans comparaison
                 systématique entre les coûts d'acquisition intégrés au budget
                 d’équipement et ceux associés à la LLD, financée par le budget de
                 fonctionnement, et sans analyse de l'impact de ces choix sur les
                 finances des collectivités territoriales concernées ;
         •      En ce qui concerne l'exploitation et l'utilisation, les modèles de
                gestion actuels ne reposent pas sur des règlements internes, des
                mécanismes organisationnels ou des procédures claires pour
                encadrer l'utilisation du parc. La gestion repose principalement sur
                des décisions individuelles des responsables, ce qui peut conduire
                à une utilisation inappropriée du parc et à une exploitation à des
                fins non administratives, entraînant ainsi une augmentation des
                coûts d'exploitation ;
         •      Quant aux opérations de maintenance et de réparation, 88%
                des collectivités n'ont pas de programme annuel de maintenance et
                de réparation, et 96% n'ont pas élaboré de manuel des procédures
                spécifique pour ces opérations. De plus, 37% des collectivités
                territoriales ne disposent pas de locaux pour protéger le parc contre
                la détérioration, tandis que les 63% restants disposent de locaux
                qui n’obéissent pas aux normes de sécurité nécessaires ;
         •      En ce qui concerne la mise en réforme des véhicules et engins,
                il a été constaté une lenteur dans la procédure suivie, ainsi que des
                divergences dans les critères appliqués d'une collectivité
                territoriale à l'autre.
     En résumé, la Cour a constaté que les pratiques actuelles de gestion du parc
     de véhicules et d'engins des collectivités territoriales révèlent un manque
     d'efficacité et entravent une utilisation optimale de ce parc. En effet, ces
     pratiques réduisent son rôle à celui d’un simple "moyen de transport", sans
     tenir compte, ainsi, de sa fonction essentielle de support à l'exercice des
     attributions des collectivités territoriales.
     Sur la base de ce qui précède, la Cour des comptes a recommandé au
     ministère de l’intérieur de mettre en place un cadre juridique,
     institutionnel et organisationnel clair, intégré et actualisé, qui régit la
     gestion du parc de véhicules et d’engins en ce qui concerne ses composants
     et ses catégories, ainsi que les modalités de son exploitation. Ce cadre
     devrait inclure des critères clairs et obligatoires pour la désignation


        Rapport annuel de la Cour des comptes au titre de 2023-2024
96                    - Principaux axes -
exclusive des personnes à qui ces véhicules sont attribués
individuellement. Elle a également recommandé d’adopter des pratiques
économiques lors des acquisitions, en utilisant tous les mécanismes de
concurrence possibles, ainsi que de généraliser l’utilisation des vignettes
et d'encadrer les opérations de location longue durée.
En outre, la Cour a recommandé au ministère de l’intérieur de veiller
à ce que les collectivités territoriales adoptent une politique d'acquisition
claire, prenant en compte les principes de l'économie et de la précision dans
la définition des besoins. Cela passerait par l’adoption de critères rigoureux
permettant une identification rationnelle des besoins en véhicules et en
engins, en fonction des priorités liées à l’exercice des compétences et à la
continuité des services publics, tout en veillant à rationaliser l’exploitation
des composantes du parc automobile.


   Les prestations d’études techniques des collectivités
                      territoriales :
    Un cadre juridique non actualisé et des déficiences dans la
   définition des besoins et dans le suivi, affectant la qualité des
          résultats des études et limitant leur exploitation

Les collectivités territoriales, les agences régionales d’exécution des
projets (AREP) et les sociétés de développement local (désignées ci-après
par les collectivités territoriales et leurs organismes) font appel à des
bureaux d'études pour élaborer des études techniques et assurer le suivi de
l'exécution des projets visant le développement de leur territoire, le
désenclavement de la population et la réalisation des infrastructures et des
équipements de base. Durant la période 2019-2023, ces collectivités
territoriales et leurs organismes ont réalisé un total de 8.007 études
techniques pour un montant de 1.167,06 MDH, en concluant 1.394
marchés publics pour un montant de 731,63 MDH et en émettant 6.613
bons de commande pour un montant de 435,43 MDH.
Ces études ont concerné plusieurs domaines de développement, dont le
plus important est celui des routes et des pistes avec 32% du nombre total
des études techniques réalisées (2.557 études) et 24% de leur montant
(276,40 MDH), suivi du domaine de l’aménagement urbain et des
équipements communaux avec 22% du nombre total (1.776 études) et 36%
de leur montant (423,23 MDH). Le domaine des bâtiments, quant à lui,
représente 17% du nombre total (1.353 études) et 12% de leur montant
(145,64 MDH), suivi de celui de l’adduction en eau potable avec 10,2% du
nombre total (816 études) et 5,9% de leur montant (68,76 MDH).


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              97
     À cet égard, les Cours régionales des comptes ont relevé, dans le cadre
     d'une mission thématique couvrant toutes les régions, plusieurs constats
     concernant le cadre juridique et réglementaire encadrant ces prestations
     d’études, les conditions d'exécution des dépenses publiques y afférentes et
     l’exploitation des livrables de ces études.
     En ce qui concerne le cadre légal et réglementaire, un ensemble de textes
     juridiques encadrant les prestations d’études n'a pas été mis à jour pour
     s’adapter aux évolutions continues de ce secteur. Il s’agit, à titre
     d’exemples, du cahier des clauses administratives générales applicables
     aux marchés de services portant sur les prestations d’études et de maîtrise
     d’œuvre passés pour le compte de l’État, le cahier des prescriptions
     communes applicables aux études routières, le cahier des prescriptions
     communes applicables aux missions réalisées par les bureaux d’études
     techniques dans le domaine du bâtiment et d’équipements publics, ainsi
     que le règlement de construction parasismique applicable aux bâtiments.
     En outre, il a été constaté l'absence d'un système d’information intégré avec
     celui de la Caisse nationale de sécurité sociale (CNSS) et mis à jour
     régulièrement, permettant à la commission d’agrément de vérifier
     l'exactitude des données concernant les employés des demandeurs
     d’agrément, déclarées auprès de la CNSS. De plus, les contrôles effectués
     par cette commission restent insuffisants et nécessitent un renforcement
     par des inspections périodiques et inopinées des bureaux d’études agréés,
     tout au long de la durée de validité de l’agrément. Il a été également
     observé l'absence d'un cadre de référence ainsi qu'une matrice des
     responsabilités, précisant les intersections entre les bureaux d'études et les
     autres professionnels des travaux publics, afin de faciliter la
     compréhension commune de leurs rôles et responsabilités, notamment dans
     les domaines concernés par les commandes publiques exécutées par les
     collectivités territoriales.
     En ce qui concerne les conditions de réalisation des prestations relatives
     aux études techniques, il a été constaté que les ressources humaines
     techniques des collectivités territoriales restent limitées, ce qui impacte
     négativement leur capacité à réaliser des études techniques en s'appuyant
     sur leurs propres moyens. De plus, le recours excessif aux bons de
     commande, par rapport aux appels d'offres, ne peut être justifié par la seule
     référence à l'urgence, sur laquelle ces collectivités se fondent. En outre, les
     projets concernés par les études techniques et leurs composantes ainsi que
     l'estimation du coût de ces études, ne sont pas suffisamment déterminés
     avant le lancement des appels d’offres.
     Dans le même contexte, les collectivités territoriales et leurs organismes
     s'appuient principalement sur le critère du niveau de qualification des


        Rapport annuel de la Cour des comptes au titre de 2023-2024
98                    - Principaux axes -
experts proposés, pour évaluer les offres techniques des concurrents. A ce
titre, il a été constaté que l'évaluation de ce critère se fait uniquement sur
la base des curriculums vitae et des diplômes universitaires attestant la
formation de chaque expert proposé, sans possibilité de vérifier l'exactitude
et la fiabilité des informations contenues dans ces documents, ni
l'appartenance réelle de ces experts aux bureaux d’études concurrents.
S’agissant de la qualité de la méthodologie proposée, l’évaluation ne se fait
pas souvent sur la base de critères objectifs, selon une grille de notation
claire et précise.
En outre, le critère du degré de transfert des connaissances n'est pas pris en
compte, malgré son importance cruciale pour renforcer les capacités
professionnelles et techniques des ressources humaines des services des
collectivités territoriales, particulièrement dans un contexte marqué par un
déficit quantitatif et qualitatif de ces ressources qualifiées.
Sur un autre registre, certaines collectivités territoriales exigent que les
concurrents possèdent des certificats d’agrément couvrant plusieurs
domaines, bien qu'elles ne maîtrisent pas toujours les dispositions
réglementaires les régissant. Cela peut conduire à obliger les bureaux
d'études à fournir des certificats d’agrément non pertinents au vu de l’objet
de l'étude envisagée, ce qui peut limiter la concurrence, d’une part, en
empêchant certains concurrents de soumettre leurs offres, et d’autre part,
en excluant d'autres, faute de disposer de l'agrément requis, bien qu'il ne
soit pas nécessaire pour la réalisation de l'étude.
Par ailleurs, il a été constaté que les commandes publiques relatives aux
prestations d’études techniques sont concentrées sur un nombre limité de
bureaux d'études. En effet, seulement 7% des bureaux d'études ayant
obtenu des marchés publics relatifs à ces prestations, y compris les
groupements, ont remporté 34% du nombre total de ces marchés, soit 33%
de leur montant. En ce qui concerne les bons de commande, seulement 2%
des bureaux d'études ont bénéficié de 24% du nombre total de ces
prestations, soit 24% de leur montant. Les commandes publiques,
attribuées à un nombre limité de bureaux d’études, concernent parfois des
collectivités territoriales éloignées et situées dans différentes régions sur
des périodes rapprochées, ce qui soulève la question de la capacité des
bureaux concernés à exécuter l’ensemble des prestations, qui leurs sont
confiées, dans les délais impartis et avec la qualité requise.
En ce qui concerne l'exécution des prestations relatives aux études
techniques, des délais raisonnables et appropriés ne sont pas alloués pour
la réalisation de ces prestations, en particulier celles effectuées par bons de
commande. Les collectivités territoriales et leurs organismes ne définissent
pas précisément les composantes, les spécifications et les contenus des


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              99
      livrables des études techniques réalisées. De plus, ils ne procèdent pas à
      une vérification, ni à un examen détaillé de ces livrables, pour s'assurer de
      leur conformité aux normes et exigences stipulées au niveau des cahiers
      des charges, cependant, ils se contentent d’une vérification administrative
      en vue de déclarer la réception de ces prestations.
      Il a également été relevé que les bureaux d'études contractés ne suivent pas
      et ne contrôlent pas régulièrement ces travaux, ou qu'une seule et même
      personne du bureau d'études assure le suivi et le contrôle des travaux sans
      la participation d'autres membres de l'équipe d'étude à ces opérations. En
      outre, les collectivités territoriales et leurs organismes ne veillent pas à
      préciser la nature des prix (unitaire ou forfaitaire) des phases des études
      d’une manière claire, en fonction de leur progression et de la mise en œuvre
      de leurs livrables, et ne garantissent pas une répartition efficace du mode
      de règlement en fonction de l'avancement de ces études.
      En ce qui concerne l'exploitation des résultats des études techniques, il
      a été constaté une disparité entre les régions quant au taux des projets,
      réalisés ou en cours de réalisation, issus des études techniques. Ce taux
      varie, au niveau de huit (8) régions, entre 20% et 92%. Il a également été
      observé que des études ont été réalisées sans qu'aucun projet d'équipement
      n'en découle. Elles représentent un montant dépassant 103,81 MDH, et se
      répartissent entre 101 marchés pour un montant de 89,14 MDH et 153 bons
      de commande pour un montant de 14,67 MDH. En outre, des modifications
      continues ont été apportées aux marchés de travaux pendant leur exécution,
      en raison du manque de précision dans la préparation des livrables des
      études techniques concernées.
      Par ailleurs, en raison de l'absence ou de l'insuffisance des crédits pour
      réaliser les projets d'équipement, les collectivités territoriales se trouvent
      parfois contraintes de réaliser des études techniques et de les soumettre à
      d'autres instances en vue de rechercher un financement partiel ou total pour
      ces projets, et ce, en l'absence d’assurances raisonnables quant à la
      possibilité de réalisation des projets en question. À cet effet, les régions,
      préfectures et provinces, au niveau de sept (7) régions, ont reçu un total de
      226 études techniques réalisées au niveau des communes, préfectures et
      provinces de ces régions, pour un montant de 158,39 MDH, afin de trouver
      des financements pour la réalisation des projets d'équipement
      correspondants. Cependant, 129 études, pour un montant de 133,03 MDH,
      n'ont pas été traduites en projets, soit 57% en termes de nombre et 84% en
      termes de montant financier.
      De plus, certaines collectivités territoriales envoient parfois les mêmes
      études à plusieurs parties simultanément, ce qui peut conduire au
      lancement des travaux du même projet par différentes entités, sans


         Rapport annuel de la Cour des comptes au titre de 2023-2024
100                    - Principaux axes -
coordination entre elles. En outre, les instances publiques destinataires de
ces études techniques n'impliquent pas les collectivités territoriales, ayant
envoyé ces études, dans les différentes étapes de réalisation des projets
d'équipement.
Eu égard à ce qui précède, la Cour des comptes a recommandé au
ministère de l’équipement et de l’eau et au ministère de l’économie et
des Finances de mettre à jour les textes législatifs relatifs aux prestations
d'études techniques et d'y inclure tous les aspects pratiques qui s’y
rapportent, ainsi que de veiller à mettre en place un référentiel des prix
pour ces prestations, afin d’apporter l’appui nécessaire au maître d'ouvrage
pour estimer efficacement le coût des prestations programmées.
En outre, la Cour a recommandé au ministère de l’intérieur de
renforcer les ressources humaines des collectivités territoriales et de
développer leurs capacités professionnelles, en particulier pour les
communes rurales, et ce en vue d’une gestion efficace des différentes
étapes de l'exécution des commandes publiques relatives aux études.
De plus, la Cour des comptes a recommandé au ministère de
l’intérieur d’inciter les collectivités territoriales et leurs organismes à
inclure des critères objectifs, mesurables et évaluables, y compris la
pondération technico-financière, ainsi que le seuil d’admissibilité des
offres, afin de garantir l'obtention de l'offre la plus économiquement
avantageuse. Elle a également recommandé d’adopter des délais
raisonnables pour la réalisation des études en fonction de leurs objets et de
la nature de leurs livrables, avec une définition précise et détaillée du
contenu de ces livrables afin de contrôler leur qualité et leur pertinence
avec les besoins des collectivités territoriales et de leurs organismes, avant
le lancement des projets concernés. De même, la Cour a insisté sur la
nécessité de veiller à ce que les bureaux d'études respectent toutes leurs
obligations contractuelles, stipulées dans les cahiers des charges, en
matière de suivi et de contrôle des travaux des projets d'équipement, tout
en veillant à s’assurer, avant la réalisation des études techniques, de la mise
en place de garanties pour l'exécution des projets concernés, et à établir des
mécanismes de coordination efficaces et efficients entre les différents
intervenants afin de traduire les études techniques réalisées en projets
d'équipement.




                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              101
                 La gestion des fourrières communales dans la
                          région Casablanca-Settat :
           Services nécessitant davantage d’encadrement juridique et
                de modernisation des modes de fonctionnement

      Les fourrières sont considérées comme des services communaux vitaux
      étant donné leur importance consistant à permettre aux présidents de
      communes d’exercer certaines de leur compétences en matière de police
      administrative, à générer des recettes financières naissant des droits de
      fourrière et de la vente des objets mis en fourrière non retirés dans les délais
      impartis, et à procurer des services aux pouvoirs et administrations publics
      ordonnant la mise en fourrière.
      Selon les données recueillies auprès des préfectures et provinces de la
      région de Casablanca- Settat, cette dernière dispose de 94 fourrières situées
      dans 86 communes et occupant une superficie globale dépassant 33
      hectares. Dans ce cadre, la Cour régionale des comptes (CRC) de la région
      de Casablanca- Settat a mené une mission, qui a concerné un échantillon
      de 31 fourrières situées dans 21 communes, et qui a porté sur l'évaluation
      des modalités de gestion de ce service, y compris les aspects afférents aux
      opérations de remorquage et de mise en fourrière.
      Concernant l’évaluation des modes de création, d’aménagement et
      d’organisation des fourrières communales, la CRC a constaté
      qu’environ 97% des fourrières ne disposent pas d’arrêtés de création en
      tant que service public conformément aux dispositions de la loi organique
      relative aux communes (n°113-14), d’autant plus que les communes
      concernées ne détiennent que de 34% de la superficie globale occupée par
      les fourrières de la région Casablanca- Settat, alors que les 66% restantes
      sont propriétés de parties tierces (Etat : 51%, privé 14%, terres collectives :
      1%).
      S’agissant de l’aménagement des fourrières, la CRC a relevé que 76% des
      fourrières sont des terrains non aménagés et que 60% d’entre elles ne
      disposent pas de compteurs d’eau et d’électricité alors que 95% des
      fourrières de la région ne sont pas dotés de panneaux de signalisation
      permettant d’organiser la circulation dans leurs enceintes.
      Quant à l’organisation des fourrières, il a été constaté que toutes les
      communes ne disposent pas d’arrêtés réglementaires régissant les
      opérations et les procédures nécessaires à la gestion des fourrières en
      particulier la délimitation de l’opération du dépôt et du retrait des véhicules
      et engins mis en fourrière et leur placement selon leur nature.



         Rapport annuel de la Cour des comptes au titre de 2023-2024
102                    - Principaux axes -
Il a été également relevé l’absence des moyens de manutention à l’exemple
des chariot-élévateurs pour optimiser la gestion de l’espace au sein de la
fourrière et partant libérer des places supplémentaires pour y disposer les
engins nouvellement mis en en fourrière. De plus, il a été observé le non
recours au mode de guichet unique dans les fourrières pour le
recouvrement combiné du montant de l’infraction et des droits de fourrière.
De même, il a été constaté le dépôt dans les fourrières d’objets pouvant
constituer un danger sur les engins qui y sont gardés et sur les espaces
attenants aux fourrières à l’instar des bouteilles de gaz, des combustibles
et des matières plastiques inflammables.
En ce qui concerne la gestion du service d’enlèvement et remorquage,
la CRC a relevé que 98% des communes de la région ne gèrent pas le
service d’enlèvement et de remorquage des véhicules destinés aux
fourrières ce qui amené certaines parties à se livrer à cette activité, sous la
supervision des autorités ordonnant la mise en fourrière, en l’absence d’un
cadre contractuel avec les communes concernées pour l’organisation de
cette opération.
Dans le même sillage, l’analyse des données produites par le ministère du
Transport et de la Logistique et par l’Agence Nationale de la Sécurité
Routière (NARSA) a révélé que l’âge de plus de 50% de la flotte des
véhicules d’enlèvement et de remorquage dépasse 20 ans, témoignant ainsi
de sa vétusté, ce qui pourrait compromettre la continuité de ce service
d’autant plus que 30% seulement de la flotte susmentionnée dispose d’un
contrôle technique valable au 31 décembre 2023.
En matière d’évaluation des modes de gestion courante des fourrières,
il a été relevé que 22% des communes ne tiennent pas des registres relatifs
aux objets mis en fourrière, en plus de la non adoption d’un système
d’information à même de permettre la collecte, le traitement et
l’exploitation des données indispensables à une gestion rationnelle des flux
d’engins transitant par les fourrières. La CRC a aussi enregistré que 60%
des communes n’assurent aucun suivi des réclamations et plaintes
afférentes aux fourrières.
Dans le même contexte, il a été constaté que 93% des communes n’ont
contracté aucune police d’assurance pour couvrir les dommages et dégâts
éventuels pouvant affecter les objets mis en fourrière et partant engager
leurs responsabilités étant donné qu’elles en sont le gardien légal durant
leur dépôt en fourrière.
Pour ce qui est de la gestion des recettes naissant des droits de
fourrière et de la vente des objets mis en fourrière, il a été observé que
les droits de fourrière dépendent principalement des actions menées par les
autorités ordonnant la mise en fourrière (police, gendarmerie, service de


                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              103
      contrôle routier) comme suite aux infractions constatées au code de la
      route. De ce fait, les communes, connaissant un trafic routier important,
      enregistrent une activité soutenue au niveau de leurs fourrières à la suite
      des opérations de contrôle entreprises, ce qui se répercute positivement sur
      les droits de fourrière encaissés. Par ailleurs, cette recette se trouve
      directement affectée par la saturation de la capacité d’accueil de la
      fourrière et son inaptitude à recevoir des véhicules supplémentaires,
      surtout avec l’écoulement de délais conséquents sans le retrait par leurs
      propriétaires des objets mis en fourrière, ce qui impacte négativement les
      recettes pouvant être générées à ce titre.
      Concernant la vente des objets mis en fourrière, la CRC a relevé l’absence
      d’un cadre juridique régissant cette opération, et garantissant aux
      communes la possibilité de jouir du produit de la vente en toute légalité,
      surtout que ces communes sont considérées comme des gardiens de ces
      objets et non leurs propriétaires. En l’absence de cet encadrement
      juridique, les procédures et les règles diffèrent d’une commune à l’autre.
      Eu égard à ce qui précède, la Cour a recommandé au ministère de
      l’intérieur de mettre en place un cadre juridique pour le service de la
      fourrière communale explicitant et encadrant la relation entre l’ensemble
      des intervenants ainsi concernés, et organisant aussi les opérations de vente
      des objets mis en fourrière non retirés dans les délais impartis à travers la
      définition des procédures à suivre à ce niveau. Elle a aussi préconisé de
      concevoir et développer un système d’information de gestion des fourrières
      et des services offerts aux usagers et de le généraliser à l’ensemble des
      collectivités territoriales.
      En outre, la Cour a recommandé de réviser le cadre fiscal en termes de
      détermination du tarif des droits de fourrières selon la nature de chaque
      objet mis en fourrière.
      La Cour a recommandé également au ministère de l’intérieur d’inciter
      les communes à fixer des règles et des critères pratiques pour la création
      des fourrières par considération aux exigences requises pour offrir des
      services de qualité aux usagers. De même, la Cour a préconisé de réguler
      l’activité d’enlèvement et de remorquage des véhicules mis en fourrière via
      l’adoption d’un cadre contractuel encadrant la relation entre les communes
      concernées et les professionnels chargés de cette activité, et d’adopter aussi
      le mode du guichet unique pour faciliter les opérations de retrait des objets
      mis en fourrière par leurs propriétaires.
      Dans le même contexte, la Cour a recommandé de mettre en place des
      règles organisationnelles pour la gestion courante de la fourrière tant au
      niveau de la tenue numérique des registres, que du suivi de ses activités et
      du sort des réclamations et des événements afférents à ce service. La Cour


         Rapport annuel de la Cour des comptes au titre de 2023-2024
104                    - Principaux axes -
a préconisé également d’accélérer les procédures d’assurance des
fourrières contre les risques et incidents éventuels qu’elles peuvent
connaitre et ce en coordination avec les parties concernées surtout la
protection civile. La Cour a recommandé aussi d’accorder l’attention
nécessaire à l’aménagement des fourrières de manière à préserver l’état des
objets mis en fourrière et leur valeur tout en y installant les dispositifs
nécessaires à leur bon fonctionnement à l’exemple des compteurs d’eau et
d’électricité, du matériel d’extinction du feu, des bureaux et des caméras
de surveillance.


     La gestion du contentieux par les communes de la
              région de Rabat-Salé-Kénitra :
     Une gestion limitée nécessitant de prioriser les dimensions
    proactives et préventives ainsi que la protection des intérêts
     des communes, tout en veillant au suivi de l’exécution des
                    jugements et arrêts définitifs

La gestion du contentieux par les communes, qu’elles soient
demanderesses ou défenderesses, revêt une importance cruciale en raison
de l’augmentation continue du nombre de jugements et arrêts prononcés à
leur encontre, en particulier ceux les condamnant à verser des montants
importants qui dépassent souvent leurs capacités financières et les crédits
alloués à l’exécution de ces jugements.
Dans ce cadre, la Cour Régionale des Comptes de la région de Rabat-Salé-
Kénitra a réalisé une mission thématique, couvrant la période de 2017 à
2022, dans le but de diagnostiquer la situation actuelle de la gestion du
contentieux par les communes de la région, ainsi que d’évaluer leurs
vigilances à protéger leurs intérêts et à éviter de grever leurs budgets par
les dépenses y afférentes.
S’agissant de la situation du contentieux des communes de la région, le
nombre total de jugements et d’arrêts définitifs émis à l’encontre de ces
communes durant la période susmentionnée s’élève à 437 jugements, pour
un montant total avoisinant 635 MDH. L’analyse de la nature de ces
jugements/arrêts révèlent que les contentieux administratifs représentent la
part majeure, avec un pourcentage de 87,4% en termes de nombre et 99,1%
en termes de montant. Concernant l’objet de ces jugements/arrêts, les
contentieux relatifs à la voie de fait et aux dépenses publiques et
fournitures, constituent la part la plus importante représentant
respectivement 24% et 22% du nombre total, et 48% et 35% des montants
dus. Pour les jugements/arrêts rendus en faveur des communes, durant la


                                         Rapport annuel de la cour des comptes au titre de 2023-2024
                                                      - Principaux axes -                              105
      période susvisée, ils ont atteint un total de 208 jugements pour un montant
      total dépassant 21,7 MDH. Dans ce cadre, les jugements relatifs aux
      recettes représentent la part la plus importante, avec 65% en nombre et
      96% en montant.
      Au niveau de l’exécution, il a été relevé le faible taux d’exécution, par les
      communes, des jugements/arrêts définitifs, ce qui a entraîné un cumul de
      jugements/arrêts non exécutés, que ce soit ceux rendus avant 2017 ou ceux
      durant la période de 2017 à 2022. Cette situation est due essentiellement à
      l’insuffisance des crédits programmés à cet effet, puisqu’ils n’ont pas
      dépassé, durant la période 2017-2022, le taux de 25% du montant total des
      jugements/arrêts définitifs rendus durant cette période ainsi que ceux
      rendus avant 2017 et restés non exécutés.
      Par ailleurs, et malgré leur intérêt, les solutions alternatives ne sont pas
      privilégiées par la plupart des communes pour l’exécution des jugements
      prononcés à leur encontre. En effet, ces solutions pourraient alléger la
      charge financière pesant sur le budget de la commune. Dans ce cadre, il a
      été constaté que seules trois communes ont exécuté des jugements/arrêts
      définitifs dans le cadre des accords à l’amiable, durant la période 2017-
      2022, et que neuf communes ont exécuté des jugements par tranches au
      cours de la même période.
      L’accumulation des jugements/arrêts définitifs rendus contre les
      communes et non exécutés, a conduit les créanciers à recourir aux
      procédures d’exécution forcée, telles que la saisie des fonds des
      communes. Dans ce cadre, 14 communes au niveau de la région ont fait
      l’objet de saisies sur leurs fonds auprès du comptable public durant la
      période 2017-2022, pour un montant total dépassant 359 MDH. En outre,
      des cas de condamnation de l’ordonnateur au paiement d’astreintes ont été
      enregistrés au niveau de quatre communes.
      Par ailleurs, il a été constaté un recours limité aux solutions amiables pour
      régler les différends, malgré l’importance de la gestion proactive et
      préventive du contentieux dans la préservation des intérêts et des
      ressources financières des communes. En effet, entre 2017 et 2022, seules
      quatre communes ont déclaré avoir résolu certains litiges à l’amiable avant
      d’ester en justice. Concernant la coordination avec l’agent judiciaire des
      collectivités territoriales, nommé par l’arrêté du ministre de l’intérieur
      n°20.1555 du 13 juillet 2020, seules 12 communes ont fait appel à ses
      services, ce qui reflète la faible coordination avec cette institution, malgré
      l’importance de l’assistance juridique et judiciaire qu’elle peut apporter.
      En ce qui concerne la gestion administrative du contentieux, la majorité
      des communes souffrent de carence en ressources humaines. Ainsi, 72%
      des communes de la région ne disposent que d’un seul fonctionnaire chargé


         Rapport annuel de la Cour des comptes au titre de 2023-2024
106                    - Principaux axes -
de ce domaine. De plus, il a été observé une insuffisance dans la formation
continue de ces fonctionnaires. En effet, seules neuf communes ont indiqué
qu’un de leurs fonctionnaires avait bénéficié d’une formation liée au
contentieux au cours de la période 2017-2022.
L’ensemble de ces insuffisances ont entraîné, au niveau de certaines
communes, l’absence de documents relatifs aux dossiers en cours ou déjà
jugés, telles que les mémoires, les conclusions et les jugements. En outre,
il a été constaté un manque de coordination entre les différents services, ce
qui pourrait nuire à la gestion du contentieux et à la protection des intérêts
de la commune.
Au vu de ce qui précède, et dans la perspective de créer une nouvelle
dynamique interactive, la Cour des Comptes a recommandé au
ministère de l’intérieur de mettre en place une stratégie de gestion du
contentieux des collectivités territoriales, axée sur trois piliers, à savoir la
prévention du contentieux, le recours aux solutions alternatives pour régler
les différends, ainsi que la gestion efficace du contentieux en cas de
survenance.
De plus, la Cour a recommandé aux communes de prendre les mesures
nécessaires pour défendre leurs intérêts, telles que la présence de leurs
représentants aux audiences et aux sessions d’instruction, la présentation
de leurs conclusions après l’expertise, ainsi que le suivi des différentes
étapes des dossiers. Elle a également préconisé la mise en œuvre des
solutions alternatives pour résoudre les différends et le recours aux services
de l’agent judiciaire des collectivités territoriales pour bénéficier de
l’assistance juridique et judiciaire qu’il offre. En outre, la Cour a
recommandé aux communes de suivre l’exécution des jugements et des
arrêts définitifs et d’éviter leur accumulation, tout en veillant à programmer
les crédits budgétaires suffisants et à recourir, selon les cas, à l’exécution
des jugements dans le cadre d’accords à l’amiable et par tranches. De plus,
la Cour a appelé à veiller à la qualification des ressources humaines
chargées de la gestion du contentieux, en assurant leur formation continue,
et à améliorer la gouvernance de la gestion et du suivi des dossiers liés aux
contentieux, en adoptant des systèmes informatiques appropriés.




                                           Rapport annuel de la cour des comptes au titre de 2023-2024
                                                        - Principaux axes -                              107
                    Autres missions de contrôle exercées
                    par les cinq chambres sectorielles et
                      les douze Cours régionales des
                                  comptes:
                        Un impact tangible sur la gestion des affaires
                                        publiques

      Outre les missions de contrôle, objet des projets d’insertion présentés
      précédemment, les cinq chambres sectorielles de la Cour et les Cours
      régionales des comptes (CRC) ont mené, au cours de la période 2023-2024,
      d’autres missions de contrôle. Celles-ci ont eu un impact tangible sur la
      gestion publique, tant sur le plan financier que dans ses dimensions de
      gestion, sociales et environnementales.
      En ce qui concerne les cinq chambres sectorielles, elles ont réalisé six
      missions à caractère transversal et contrôlé sept organismes, en plus d'une
      mission portant sur l'emploi des fonds publics, dont certaines ont été
      menées en partenariat avec les Cours régionales concernées. Ces missions
      de contrôle sont réparties selon leur type comme suit :
           Type de
                                                                       Thématique/organisme
           contrôle
                                      Approvisionnement en médicaments des établissements de
                                      soins relevant du ministère de la santé et de la protection
                                      sociale.
                                      Recherche scientifique et technique dans les universités
         Missions à                   publiques
          caractère                   Centres de protection de l’enfance
         transversal
                                      Sport de proximité
                                      L’emploi dans les activités de gardiennage et de nettoyage
                                      Gestion du domaine public maritime
                                      Office national de l'électricité et de l'eau potable
                                      Office national du conseil agricole
                                      Ministère de la transition énergétique et du développement
        Contrôle des                  durable
        organismes                    Agences pour la promotion et le développement
                                      économique et social des préfectures et provinces du sud,
                                      du nord et de l’oriental
                                      Archives du Maroc



         Rapport annuel de la Cour des comptes au titre de 2023-2024
108                    - Principaux axes -
    Type de
                                   Thématique/organisme
    contrôle
                   Centre cinématographique marocain
                   Théâtre national mohammed V
   Contrôle de
   l'emploi des    Subventions accordées par les départements ministériels
  fonds publics
Ces missions de contrôle ont eu un impact significatif sur la gestion des
organismes concernés. En effet, en réponse aux observations et
recommandations de la Cour dans le cadre de la mission portant sur
l’emploi dans les activités de gardiennage et de nettoyage, une campagne
nationale a été lancée par l'Inspection du travail pour contrôler les
entreprises opérant dans ce domaine. De plus, une base de données a été
constituée pour répertorier les entreprises agréées dans le domaine du
gardiennage, et des dispositions spécifiques ont été introduites dans le
cadre du décret n°2.22.431 relatif aux marchés publics, qui portent à la
protection des droits sociaux des travailleurs lors de la passation des
marchés concernant les services de gardiennage et de nettoyage.
S’agissant du domaine public maritime, les parties prenantes impliquées
dans la gestion des plages ont élaboré, en juin 2023, un amendement de la
circulaire conjointe n° 9102, afin de modifier et d'ajouter certaines
dispositions facilitant sa mise en œuvre effective. De plus, en mars 2023,
un accord préliminaire a été conclu entre le ministère de l'économie et des
finances et celui chargé de l'équipement, en vue d’activer la résolution
amiable des cas de chevauchement entre le domaine public maritime et le
domaine privé de l'État. Par ailleurs, un projet de décret encadrant les
règles relatives au dragage d'entretien des embouchures des oueds a été
élaboré et soumis à la procédure d'approbation en mai 2023, mais il n'a pas
encore été adopté.
Concernant les Agences pour la promotion et le développement
économique et social des préfectures et provinces du Sud, du Nord et de
l’Oriental, une coordination est mise en place entre les départements
ministériels concernés pour appliquer les dispositions de la lettre du
ministre de l’économie et des finances, en date du 30 janvier 2017,
notamment la suspension de la programmation de tout nouveau projet au
niveau des trois agences, en attendant une décision sur leur avenir.
Quant à l’établissement Archives du Maroc, la circulaire du Chef du
gouvernement n°2/2024, en date du 4 mars 2024, a été émise pour encadrer
les opérations de destruction des archives au sein des administrations de
l'État, des collectivités territoriales, ainsi que des établissements et
entreprises publiques.


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              109
      En ce qui concerne le Centre cinématographique marocain, le projet de loi
      n°18.23 relatif à l'industrie cinématographique et à la réorganisation du
      Centre a été adopté le 12 juin 2024. En outre, un projet a été élaboré pour
      organiser la gestion de la cinémathèque, accélérer l'achèvement des
      travaux en cours, ainsi que réaffecter une partie du personnel de la
      cinémathèque vers d'autres services en attendant sa mise en exploitation.
      Par ailleurs, une méthodologie de travail a été mise en place pour assurer
      la coordination entre la division de la production et le service financier,
      dans le domaine du recouvrement des recettes.
      Enfin, en ce qui concerne les subventions accordées par les départements
      ministériels, et suite aux observations et recommandations de la Cour, un
      projet de décret a été élaboré par le ministère chargé des relations avec le
      parlement, en concertation avec les départements ministériels et les
      établissements publics concernés, afin d’organiser et d’encadrer les
      subventions destinées aux associations. En outre, un programme national
      a été conçu par ce ministère, visant à promouvoir, structurer, organiser et
      renforcer les capacités des associations de la société civile, dans le cadre
      de la nouvelle stratégie « Nassij » 2022-2026. Par ailleurs, le ministère de
      l'intérieur et celui chargé de la jeunesse ont entamé, à partir de 2023, la
      mise en place de systèmes d'information pour la gestion des dossiers des
      subventions.
      Quant aux douze CRC, elles ont réalisé, durant les années 2023-2024, un
      total de 154 missions propres, concernant 730 organismes soumis à leur
      contrôle. Parmi ces missions, 14 à caractère transversal ayant porté sur des
      thématiques relatives à la gestion des équipements et services publics
      locaux (transport public par autobus, assainissement liquide et traitement
      des eaux usées, gestion des déchets ménagers et assimilés, gestion des
      fourrières) en plus de thématiques afférentes à la planification et
      l’aménagement urbain, à l’investissement et à la protection sociale.
      Les autres missions propres, d’un nombre de 140, ont ciblé des organismes
      spécifiques (135 missions) et ont porté sur le suivi de la mise en œuvre des
      recommandations (05 missions). Ces missions propres sont réparties
      comme suit :
                                Type de contrôle                       Thématique/organisme
       Provinces et préfectures en tant que collectivités              9 missions
       territoriales
       Communes                                                        114 missions
       Contrats de gestion déléguée                                    10 missions
       Sociétés de développement local                                 2 missions
       Suivi des recommandations                                       5 missions



         Rapport annuel de la Cour des comptes au titre de 2023-2024
110                    - Principaux axes -
Ces missions de contrôle ont eu un impact immédiat sur la gestion des
organismes concernés, qui ont mis en place des mesures correctives, soit
durant l'exécution de la mission de contrôle, soit dès la réception des
rapports les concernant.
Pour ce qui est de l’l’impact financier, les organismes concernés, suite
aux observations des CRC, ont pris des mesures ayant un impact direct sur
leurs finances. Cet impact a été estimé partiellement à environ 139 MDH
obtenus par le recouvrement de créances et obligations dues (54 MDH),
l'acquittement des engagements contractuelles (78 MDH), l'application des
pénalités de retard (6,3 MDH) et la restitution de sommes indûment payées
(0,82 MDH). En outre, des mesures ont été mise en œuvre permettant le
recouvrement de créances impayées, totalisant environ 52 MDH.
Les missions de contrôle réalisées par les Cours régionales ont également
eu d'autres effets sur la gestion administrative et financière, ainsi que sur
les équipements communaux et les services fournis. Elles ont également
généré des effets à caractère social et environnemental sur les projets de
développement, dont certains ont eu des impacts indirects sur les finances
des organismes concernés.
Ces effets se manifestent, notamment, par le renforcement des mécanismes
de contrôle interne, en particulier au niveau des communes rurales, ainsi
que par l’établissement de leurs bases et principes, étant donné qu’ils
constituent un levier essentiel pour améliorer la gestion et prévenir,
éventuellement, la fraude. De plus, un ensemble de procédures a été mis
en place visant à améliorer la gestion administrative, des ressources
humaines, des ressources financières et des commandes publiques.
Les effets des missions de contrôle des CRC concernant la gestion des
projets de développement se manifestent principalement par l’accélération
de la réalisation ou l’achèvement de certains projets, grâce à la levée des
obstacles entravant leur progression. Cela comprend la mise à disposition
du foncier nécessaire, l'octroi des financements requis, ainsi que la
réalisation des études correspondantes (projets d’assainissement liquide,
de construction d'une station d'épuration des eaux usées, d'aménagement
urbain et d’implantation d’un marché hebdomadaire).
De plus, des projets à caractère social, tels que la réalisation de 19 clubs
féminins et deux maternités pour un montant global d'environ 17,4 MDH,
ont vu leurs difficultés surmontées, outre l’amélioration du taux
d’opérationnalisation d’une zone industrielle. Il a également été constaté
que le solde restant, d’un montant de 3, MDH, a été exploité dans le cadre
d'une convention conclue avec le ministère de l'intérieur, visant à
réhabiliter un bureau communal d’hygiène (agrandissement du centre de



                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              111
      médecine légale, mise à niveau et équipement du bureau communal
      d’hygiène, construction d’un chenil pour animaux, etc.).
      L'amélioration de la performance des équipements communaux et de la
      qualité des services rendus aux citoyens constitue l'une des manifestations
      les plus marquantes des effets des missions de contrôle des CRC. À cet
      égard, des progrès significatifs ont été observés, au niveau de certaines
      communes, notamment dans le domaine de l'urbanisme, où les délais de
      traitement des demandes de permis de construire et d’autorisations de
      lotissement ont été réduits, et les causes des retards dans leur traitement
      ont été surmontées. De plus, un système de gestion dématérialisée a été mis
      en place, dans certains cas, pour le suivi des demandes de réception
      provisoire des travaux de lotissements et de projets résidentiels.
      Concernant les équipements liés à l’environnement, un accord multilatéral
      a été signé pour la réutilisation des eaux usées traitées dans l’irrigation des
      espaces verts. Parallèlement, des mesures ont été engagées, par certaines
      communes, pour élaborer le plan communal de gestion des déchets, lancer
      la construction d’une décharge et d’un centre de valorisation des déchets,
      ainsi que renforcer les moyens mis à la disposition des services chargés du
      suivi de la gestion des installations de propreté, outre des actions menées
      pour éradiquer plusieurs points noirs. Enfin, des programmes
      d’intervention pour la police administrative en matière de santé publique
      ont été mis en place, accompagnés de décisions communales visant à
      réglementer le domaine de l’hygiène et de la santé publique.
      En relation avec l’aménagement du territoire, de vastes campagnes ont été
      menées, parallèlement aux missions de contrôle, au niveau de plusieurs
      communes, visant à libérer le domaine public maritime des occupations
      illégales et des constructions non autorisées. De plus, il a été relevé
      l’accélération de la cadence d’élaboration des documents d’urbanisme,
      ainsi que des plans et schémas de protection de l'environnement, du littoral
      et de la mobilité durable, outre l'intégration des principes de durabilité dans
      la planification urbaine.
      Concernant la gestion du transport scolaire en milieu rural au niveau de
      certaines provinces, des démarches ont été engagées pour créer une société
      de développement local afin d'assurer une gestion plus performante du
      service. Cette initiative vise également à améliorer la gouvernance du
      transport scolaire, notamment par la mise en place d’une base de données
      et la création de comités de suivi conjoints, afin de garantir un meilleur
      suivi de sa gestion.




         Rapport annuel de la Cour des comptes au titre de 2023-2024
112                    - Principaux axes -
             Suivi de la mise en œuvre des
                   recommandations
À l’instar de l'année précédente, la Cour des comptes a poursuivi le suivi
de la mise en œuvre de ses recommandations par la plateforme
électronique, opérant depuis le 29 juin 2022. Ce suivi a concerné
l'ensemble des recommandations émises dans le cadre des missions de
contrôle réalisées au titre des programmes annuels de la Cour pour la
période 2021-2023, totalisant 616 recommandations issues de 55 missions
de contrôle. En outre, la Cour a continué à suivre les recommandations
partiellement réalisées ou non entamées, émises dans le cadre des missions
de contrôle au titre des années 2019-2020, selon la nouvelle approche
adoptée par la Cour qui prévoit un suivi pour chaque recommandation,
année après année, jusqu'à sa mise en œuvre complète, sauf en cas de
survenue de nouvelles circonstances rendant la recommandation sans
objet. A cet égard, elle a continué le suivi pour 355 recommandations
issues de 49 missions de contrôle.
Concernant les Cours régionales des comptes (CRC), des supports écrits
sur la base de formulaires et de questionnaires (suivi documentaire) sont
toujours utilisés pour suivre la mise en œuvre des recommandations
émises. Le suivi a concerné celles notifiées au titre des missions de contrôle
réalisées dans le cadre des programmes de travaux de 2021 et 2022, et ce,
dans l’attente de la généralisation progressive de la plateforme électronique
aux collectivités territoriales.
     I.     Suivi de la mise en œuvre des recommandations émises par
            la Cour des comptes
La Cour a procédé au suivi de la mise en œuvre de 971 recommandations
émises dans le cadre de 104 missions de contrôle de la gestion, d'évaluation
des programmes et projets publics, ainsi que de contrôle de l’emploi des
fonds publics, réalisées dans le cadre des programmes annuels pour la
période 2019-2023.
          1. Réalisation de 18% des recommandations programmées à
             être mises en œuvre avant fin 2023 et 42% partiellement
             réalisées
La Cour a constaté que seulement 18% des 278 recommandations dont la
mise en œuvre a été programmée avant la fin de l'année 2023, soit 49
recommandations, ont été entièrement appliquées, représentant une
augmentation de trois points par rapport au pourcentage constaté dans le
rapport de la Cour 2022-2023. Par ailleurs, 116 recommandations sont


                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              113
      partiellement réalisées (42%), tandis que la mise en œuvre de 113
      recommandations (40%) n'a pas encore été entamée.
      Cette situation s'explique, selon les réponses des organismes concernés,
      par plusieurs facteurs, notamment le lien entre la réalisation de certaines
      recommandations avec l’achèvement de programmes et réformes
      stratégiques nécessitant un temps de mise en œuvre prolongé ainsi qu'une
      coordination des efforts entre divers secteurs ou organismes publics. De
      plus, certaines recommandations dépendent de l'exécution d'autres
      chantiers, tandis que d’autres revêtent un caractère légal ou institutionnel,
      rendant leur mise en œuvre soumise aux contraintes du temps législatif ou
      réglementaire. Cette situation résulte également du manque de mesures
      prises pour mettre en œuvre certaines recommandations, ainsi que des
      contraintes rencontrées en raison de l'augmentation importante du nombre
      de recommandations objets de suivi dans la plateforme, soit plus de 174%.
      En dépit du faible pourcentage de recommandations entièrement réalisées,
      la Cour a noté des effets positifs sur la gestion des affaires publiques, se
      manifestant dans plusieurs domaines clés, notamment la gouvernance
      territoriale, les finances publiques, le secteur de la santé, les services offerts
      aux citoyens, ainsi que la gestion du soutien public accordé aux
      associations.
      À titre d’illustration, en réponse à la recommandation de la Cour
      concernant l'élaboration d'une stratégie claire pour la création et la
      dissolution des filiales, l'Agence d'Aménagement de la Vallée du
      Bouregreg a indiqué avoir entamé les procédures nécessaires à la
      dissolution des filiales inactives. L’Agence a précisé que deux sociétés ont
      été concernées par cette mesure, et les chargés de la procédure de la
      liquidation ont été nommés respectivement en novembre 2021 et juin 2022.
      L'Agence a également signalé la réalisation d’une étude pour évaluer la
      situation de ses filiales et que les résultats de cette étude ont été présentés
      à l’assemblée générale de cette société et au conseil d'administration de
      l’Agence. De plus, dans le cadre de la mise en œuvre de sa nouvelle
      organisation, l'Agence a évoqué la création d’une division dédiée à l'audit
      et au suivi, afin de renforcer le système de contrôle interne des filiales.
              2. Nécessité de renforcer l'interaction et l’implication des
                 parties concernées par la mise en œuvre d’importantes
                 recommandations liées à des chantiers nationaux
      Le Cour a constaté que de nombreuses recommandations importantes
      concernant des chantiers stratégiques d’envergure nationale n'ont pas été
      pleinement mises en œuvre, ce qui nécessite une mobilisation et un
      engagement accrus de la part des départements ministériels concernés,
      pour en garantir la mise en œuvre.


         Rapport annuel de la Cour des comptes au titre de 2023-2024
114                    - Principaux axes -
Cela concerne, à titre d’exemple, le chantier de la régionalisation avancée,
notamment la recommandation visant l'accélération de l'élaboration et de
l’adoption des décrets relatifs à la mise en place de représentations
administratives régionales communes de l'État, ainsi que la
recommandation relative à l'activation des compétences partagées entre
l'État et les régions. Il en va de même pour le chantier de la généralisation
de la protection sociale, notamment les deux recommandations portant sur
le développement des établissements hospitaliers publics comme principal
levier du système de couverture sanitaire de base, ainsi que sur le contrôle
du secteur privé selon une approche visant à poser les bases d’un système
de santé national unifié, où toutes les composantes œuvrent à concrétiser
la politique de l'État dans le domaine de la santé. Relativement à la mission
d'évaluation des dépenses d'investissement inscrites au budget général de
l'État, il a été noté que la recommandation concernant la création d'une
banque de projets et d'une base de données relative aux projets
d'investissement, soutenue par un système d'information pour le suivi et
l'aide à la décision, ainsi que la recommandation relative au renforcement
du mécanisme de gouvernance des transferts et des subventions accordées
par l'État aux établissements publics pour améliorer l'efficacité des
dépenses d'investissement, n'ont pas été mises en œuvre.
    II.   Suivi de la mise en œuvre des recommandations émises par
          les Cours régionales des comptes
Le nombre de recommandations émises par les Cours régionales des
comptes a atteint un total de 3.523 recommandations, dans le cadre de 236
missions de contrôle portant sur les organismes soumis à la compétence
des cours régionales.
      1. Réactivité des organismes concernés : 47% des
         recommandations ont été entièrement mises en œuvre,
         avec une amélioration relevée dans la gestion des
         équipements publics, des recettes et des marchés publics
En se basant sur le suivi documentaire de la mise en œuvre des
recommandations, les Cours régionales des comptes ont constaté que 47%
des recommandations émises ont été pleinement mises en œuvre,
enregistrant ainsi une légère baisse de cinq points par rapport au taux de
mise en œuvre figurant dans le rapport annuel 2019-2020. Par ailleurs, le
pourcentage de recommandations partiellement réalisées a atteint 36%,
tandis que la mise en exécution de 17% des recommandations n’a pas
encore été entamée.
Les recommandations mises en œuvre ont eu un impact positif,
principalement observé à travers l'amélioration relevée dans la gestion de



                                          Rapport annuel de la cour des comptes au titre de 2023-2024
                                                       - Principaux axes -                              115
      certains services publics, ainsi que dans la gestion des recettes et des
      marchés publics. À titre d’exemple, pour les recommandations relatives
      aux contrats de gestion déléguée de la collecte des déchets ménagers et
      assimilés dans plusieurs communes de la région Fès-Meknès, la rédaction
      et la clarté des clauses contractuelles ont été améliorées, en réponse aux
      recommandations de la Cour régionale. Ces mesures ont permis de réduire
      les coûts annuels des contrats en vigueur de 25% par rapport aux contrats
      antérieurs, ce qui représente une économie totale de 44.516.543,89 dirhams
      sur sept ans de mise en œuvre desdits contrats. De plus, des conventions
      ont été signées avec les entreprises délégataires pour obtenir des
      compensations financières en raison du non-respect de certaines clauses
      contractuelles, pour un montant total de 9.050.984,99 dirhams. Cette action
      fait suite aux recommandations de la Cour régionale visant à rétablir
      l'équilibre financier des contrats expirés au profit des communes.
      Sur un autre registre, les organismes concernés ont justifié la non-
      exécution de certaines recommandations par diverses contraintes,
      notamment les défis liés à la coordination entre les parties impliquées dans
      la mise en œuvre des recommandations, ainsi que les ressources financières
      et humaines limitées.
              2. Suivi de la mise en œuvre des recommandations émises
                 dans le cadre des missions thématiques conjointes
      Les Cours régionales des comptes ont procédé au suivi des
      recommandations formulées à l’issue de plusieurs missions thématiques
      conjointes, axées sur des enjeux d’envergure horizontale et revêtant une
      importance cruciale pour l'amélioration de la gestion publique et de la
      qualité des services rendus aux citoyens. À ce niveau, il a été constaté que
      seulement 6% des recommandations émises ont été entièrement mises en
      œuvre (5 recommandations sur un total de 83), 51% ont été partiellement
      réalisées (42 recommandations), tandis que l’application de 43% des
      recommandations n'a pas encore été entamée (36 recommandations).
      A titre d’exemple, en ce qui concerne la mission thématique portant sur les
      aspects les plus importants de la gestion des communes en milieu rural, des
      efforts ont été entrepris pour mettre en œuvre la recommandation relative
      à la création d’organismes publics régionaux ou inter collectivités
      territoriales chargés de la distribution d'eau potable au profit des
      populations rurales. À cet égard, le Ministère de l'Intérieur a précisé que la
      loi n°83.21 relative à la création des entreprises régionales multiservices a
      été promulguée le 12 juillet 2023, accompagnée des décrets d'application
      nécessaires, ainsi que d'une décision du ministre de l'Intérieur définissant
      le contrat de gestion type et les cahiers des charges y associés. Le ministère
      a ajouté que la création des dites entreprises sera faite de manière


         Rapport annuel de la Cour des comptes au titre de 2023-2024
116                    - Principaux axes -
progressive en trois étapes et qu’il a pris les dernières mesures pour le
lancement de la première phase de création desdits organismes pour les
régions de Casablanca-Settat, de l'Orient, de Marrakech-Safi et de Souss-
Massa.
Cependant, la Cour a noté la non-mise en œuvre de nombreuses
recommandations essentielles, notamment celle émise dans le cadre de la
mission thématique précitée et visant à garantir l'entretien régulier des
routes et des pistes, selon un programme préalablement élaboré qui définit
les besoins et les priorités. Il en est de même pour la recommandation
concernant la gestion des souks hebdomadaires, qui a insisté sur
l'accélération de la promulgation des textes réglementaires nécessaires à
l'application des dispositions de la loi n°54.05 relative à la gestion déléguée
des services publics, afin d'unifier et de maîtriser les pratiques en matière
de mise en jeu de la concurrence.                                     
"""
    conversation_history = StreamlitChatMessageHistory()  # Créez l'instance pour l'historique

    st.header("Explorez le rapport annuel de la Cour des comptes au titre de 2023 - 2024 à travers notre chatbot💬")
    
    # Load the document
    #docx = 'PLF2025-Rapport-FoncierPublic_Fr.docx'
    
    #if docx is not None:
        # Lire le texte du document
        #text = docx2txt.process(docx)
        #with open("so.txt", "w", encoding="utf-8") as fichier:
            #fichier.write(text)

        # Afficher toujours la barre de saisie
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)
    selected_questions = st.sidebar.radio("****Choisir :****", questions)
        # Afficher toujours la barre de saisie
    query_input = st.text_input("", key="query_key",placeholder="Posez votre question ici...", help="Posez votre question ici...")
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)

    if query_input and query_input not in st.session_state.previous_question:
        query = query_input
        st.session_state.previous_question.append(query_input)
    elif selected_questions:
        query = selected_questions
    else:
        query = ""
    predefined_question = "Donnez-moi un résumé du rapport"

    loading_message = st.empty()

    if query :
        st.session_state.conversation_history.add_user_message(query) 
        # Vérifier si la question de l'utilisateur contient la question prédéfinie
        if predefined_question.lower() not in query.strip().lower():
        # Afficher le message de "Génération de la réponse" si la question est différente
            loading_message.text("Génération de la réponse...")
            st.markdown('<div class="loading-message"></div>', unsafe_allow_html=True)

        

        if "Donnez-moi un résumé du rapport" in query:
            summary="""Le rapport annuel 2023-2024 de la Cour des comptes du Maroc met en lumière les principales réformes et défis auxquels le pays est confronté dans un contexte mondial marqué par des tensions économiques et climatiques. Il souligne une amélioration des indicateurs économiques, notamment une croissance de 3,4 % et une baisse du déficit budgétaire à 4,4 % du PIB en 2023, grâce à des efforts fiscaux et des réformes structurelles. Cependant, des défis persistent, tels que le stress hydrique, l'optimisation des investissements publics, et la digitalisation insuffisante de l'administration. Le rapport met également en exergue des lacunes dans la gestion des ressources et propose des recommandations pour améliorer l'efficacité des dépenses publiques, la gouvernance et l'impact des réformes sur le citoyen."""
            st.session_state.conversation_history.add_ai_message(summary) 

        else:
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"{query}. Répondre à la question d'apeés ce texte repondre justement à partir de texte ne donne pas des autre information voila le texte donnee des réponse significatif et bien formé essayer de ne pas dire que information nest pas mentionné dans le texte si tu ne trouve pas essayer de repondre dapres votre connaissance ms focaliser sur ce texte en premier: {text} "
                    )
                }
            ]

            # Appeler l'API OpenAI pour obtenir le résumé
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # Récupérer le contenu de la réponse

            summary = response['choices'][0]['message']['content']
           
                # Votre logique pour traiter les réponses
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(response)
            st.session_state.conversation_history.add_ai_message(summary) 
              
            #query_input = ""

            loading_message.empty()


 # Ajouter à l'historique
            
            # Afficher la question et le résumé de l'assistant
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(summary)

            # Format et afficher les messages comme précédemment
                
            # Format et afficher les messages comme précédemment
        formatted_messages = []
        previous_role = None
        if st.session_state.conversation_history.messages:
        # Parcourir les messages de manière inversée par paire (question, réponse)
            messages_pairs = zip(reversed(st.session_state.conversation_history.messages[::2]), 
                             reversed(st.session_state.conversation_history.messages[1::2]))

            for user_msg, assistant_msg in messages_pairs:
                role_user = "user"
                role_assistant = "assistant"
            
                avatar_user = "🧑"
                avatar_assistant = "🤖"
                css_class_user = "user-message"
                css_class_assistant = "assistant-message"
 
            # Formater et afficher la question de l'utilisateur et la réponse de l'assistant
                message_div_user = f'<div class="{css_class_user}">{user_msg.content}</div>'
                message_div_assistant = f'<div class="{css_class_assistant}">{assistant_msg.content}</div>'

                avatar_div_user = f'<div class="avatar">{avatar_user}</div>'
                avatar_div_assistant = f'<div class="avatar">{avatar_assistant}</div>'

                formatted_message_user = f'<div class="message-container user"><div class="message-avatar">{avatar_div_user}</div><div class="message-content">{message_div_user}</div></div>'
                formatted_message_assistant = f'<div class="message-container assistant"><div class="message-content">{message_div_assistant}</div><div class="message-avatar">{avatar_div_assistant}</div></div>'

                formatted_messages.append(formatted_message_user)
                formatted_messages.append(formatted_message_assistant)
          
        # Afficher les messages formatés
            messages_html = "\n".join(formatted_messages)
            st.markdown(messages_html, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
