from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from datetime import datetime
import numpy as np

# ✅ 모델 로드 (최초 한 번만)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Elasticsearch 연결
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'elastic'),
    verify_certs=False  # 개발 환경에서는 False, 운영 환경에서는 반드시 True
)

# ✅ description을 임베딩하는 함수
def get_embedding_from_description(text: str) -> list:
    embedding = embedding_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

# 의성군 관광지 데이터
UISEONG_ATTRACTIONS = [
    {
        "id": 1,
        "name": "이계당",
        "category": "cultural_heritage",
        "type": "cultural_heritage",
        "lat": "36.4018742624171",
        "lng": "128.775087366761",
        "description": "이계당은 이계伊溪 남몽뢰南夢賚가 효종 2년1651에 세워서 학문을 닦던 서재이다. 불이 나서 모두 타버렸는데 정조 9년1785에 다시 지어 오늘에 이르고 있다."
    },
    {
        "id": 2,
        "name": "대곡사 명부전",
        "category": "temple",
        "type": "temple",
        "lat": "36.4902176629319",
        "lng": "128.377686294996",
        "description": "의성대곡사명부전(義城大谷寺冥府殿)"
    },
    {
        "id": 3,
        "name": "대곡사 다층 석탑",
        "category": "temple",
        "type": "temple",
        "lat": "36.4902176629311",
        "lng": "128.377686294996",
        "description": "대곡사는 공민왕 17년1368에 지공指空과 혜근惠勤이 처음 세웠다."
    },
    {
        "id": 4,
        "name": "서계당",
        "category": "cultural_heritage",
        "type": "cultural_heritage",
        "lat": "36.4020722805468",
        "lng": "128.773652562134",
        "description": "義城月沼里소나무점곡면 윤암리는 1652년 남해준南海準과 그의 아들 남몽뢰南夢賚가 들어와 대대로 살면서 영양 남씨의 마을로 번성하였다. 의성 서계당은, 『의성향교지義城鄕校誌』에 따르면, 1800년대 말 남용진南瑢鎭이 세웠고, 그 손자인 남동욱南東旭이 증축하였다고 한다. 서계당은 ‘ㅡ’자형의 사랑채와 ‘ㄷ’자형의 안채가 안마당을 감싸고 있어 전체적으로 트인 ‘ㅁ’자형의 배치를 하고 있다. 안채 외부 벽체와 사랑채 사이에 벽을 두어 외부인의 시선과 출입을 막는다는 점이 독특하다. 서계당은 간략하고 소박하게 지었지만 옛날 하인들이 살던 작은 초가와 방앗간, 우물 등이 남아 있어 당시의 생활사를 연구하는 데 귀중한 자료이다."
    },
    {
        "id": 5,
        "name": "내산리 석불 좌상",
        "category": "temple",
        "type": "temple",
        "lat": "36.3530873468762",
        "lng": "128.422836856029",
        "description": """부처의 모습을 나타낸 것을 불상이라 하는데, 이 불상이 서 있는 모습이면 입상, 앉은 모습이면 좌상이라 부른다.

내산리 석불좌상을 보호하기 위하여 집을 지어 관리하다가 지금은 헐어내고 바깥에 있는 큰 바위 위에 높게 단을 만들어 남쪽을 바라보도록 두었다. 원래 있었던 장소나 내력에 대해서는 전해지는 바가 없지만 주변에 기와조각이 많고 다듬어진 돌들이 흩어져 있는 것으로 볼 때, 지금의 위치에 절이 있었던 것으로 추정한다.

내산리 석불좌상은 사암질*의 돌에 조각되었다. 머리와 손, 발 등이 크게 표현되어 있어 균형감이 떨어지고 조각 수법도 거칠고 투박하다. 어깨도 좁게 움츠려져 있으며, 법의의 옷 주름은 전체적으로 굵고 같은 간격으로 되어 있다. 고려 시대에 만들어졌지만 의성 지역의 영향을 받아 모양이나 형식이 변한 약사여래불**로 추정한다.

* 사암 : 모래가 뭉쳐서 단단히 굳어진 암석.
** 약사여래불 : 열두 가지 소원을 세워 중생의 질병 구제, 수명 연장, 재화 소멸, 의식 만족을 이루어 주며, 중생을 바른길로 인도하여 깨달음을 얻게 하는 부처."""
    },
    {
        "id": 6,
        "name": "비인 향교",
        "category": "cultural_heritage",
        "type": "cultural_heritage",
        "lat": "36.3701056059706",
        "lng": "128.471911472958",
        "description": """향교는 고려와 조선시대에 공자를 비롯한 중국과 우리나라 뛰어난 인물들의 위패*를 모시고, 유학을 가르쳐 인재를 양성하는 지방의 중등 교육기관으로서 오늘날의 국립 중고등학교와 견줄 수 있다. 제향과 교육의 두가지 기능을 담당하고 있으므로 공간의 구성도 앞쪽은 교육을 담당하는 명륜당과 동재, 서재를 두고, 뒤쪽은 제향을 담당하는 대성전과 동무, 서무를 두는 것이 일반적이다.
비안향교는 동쪽 높은 대지에 대성전을 두고 그 아래 명륜당을 세워 전학후묘(前學後廟)의 배치를 하고 있다. 대성전 앞에는 동무와 서무가 서로 마주보고 있다. 이 밖에도 광풍루, 교직사, 화장실, 연못 등이 갖추어져 있다.
비안향교가 지어진 시기는 정확히 알 수 없으나 조선시대 초기에 지어진 것으로 추정된다.
조선 후기 교육적 기능이 상실된 향교 건축물의 경우, 동·서재가 없는 곳이 있는데, 비안 향교가 이러한 예로 여겨진다. 동·서재는 없으나 제향에 관련된 건물들은 그대로 남아 있어, 조선 후기 향교의 성격을 잘 보여 주는 예로서 그 의미가 크다."""
    },
    {
        "id": 7,
        "name": "월소리 소나무",
        "category": "nature",
        "type": "nature",
        "lat": "36.493271790054",
        "lng": "128.424055761965",
        "description": """義城月沼里소나무월소리 소나무는 높이 11m, 둘레 1m이고, 나이는 200년 정도 되었다. 나무 모양은 줄기에서 세 갈래로 큰 가지가 뻗어 올라가는 모습으로, 자라는 상태는 좋다.

월소리 소나무는 조선 중기 광해군1608~1623 재위 때 평산 신씨가 월소리에 정착하면서 심었다고 전한다. 그러나 나무의 나이를 200년 정도로 추정하기 때문에 정확한 사실은 알 수 없다.

월소리 소나무는 현재 당산나무* 또는 그늘나무로 마을 주민들의 보호를 받고 있다. 자연 경관을 돋보이게 하기 위하여 심었다고 전해지는 만큼 선조들의 자연이나 풍경에 대한 사랑을 엿볼 수 있다. 가지가 사방으로 퍼져 있어 나무 아래에 넓은 그늘이 만들어지므로 동네 주민들이 쉼터로 이용하고 있다."""
    },
    {
        "id": 8,
        "name": "관덕동 석조보살좌상",
        "category": "temple",
        "type": "temple",
        "lat": "36.4314935869819",
        "lng": "128.69133780388",
        "description": """보살은 부처를 도와 중생을 구제하고 불도의 깨달음을 얻은 자로 관세음보살, 대세지보살, 보현보살, 지장보살 등 수많은 보살들이 있다.
불교가 발전함에 따라 불교의 가르침에 대한 예배의 대상으로 시각적인 조형물을 만들게 되는데, 부처를 형상화하면 불상, 보살을 형상화하면 보살상으로 부르며, 불상에 비해 보살상은 화려한 장식을 하고 있다.
의성 관덕동 석조보살좌상은 마모가 심하여 보살의 이름은 알 수 없으나 가슴 앞에 있는 목걸이와 U자형 장식, 팔찌를 통해 보살상임을 알 수 있다. 보살상의 머리카락은 작은 소라 모양을 붙여 놓은 듯한 나발(螺髮)로, 정수리에는 육계(肉髻)*가 작지만 분명하게 표현되어 있다. 한때 도괴되었던 머리를 다시 붙여 두었으나, 목에는 삼도(三道)**가 뚜렷하게 남아 있다. 안면의 훼손으로 전체적인 인상을 확인하기 어려우나, 이마는 좁은 편이고 얼굴형은 가름한 편이다.
전체적으로 결가부좌***한 신체에 나타난 안정감, 얇은 옷 속으로 비치는 부드러운 굴곡, 갸름한 얼굴 등에서 8세기 통일신라 불상의 특징이 잘 나타나고 있다. 또한 영락(瓔珞)으로 불리는 구슬장식 등 섬세한 조각 솜씨를 보여주는 불상 연구에 귀중한 자료이다."""
    },
    {
        "id": 9,
        "name": "의성향교",
        "category": "cultural_heritage",
        "type": "cultural_heritage",
        "lat": "36.348899650475",
        "lng": "128.701207296406",
        "description": """향교는 국가에서 설립하여 유학을 가르치고 인재를 기르는 지방 교육 기관으로, 지금의 중 고등학교 수준의 교육을 담당하였다. 시나 문장을 짓는 법과 유교의 경전과 역사를 가르쳤고 중국과 조선 시대의 성현에게 제사를 올렸다. 갑오개혁 이후 교육 기능은 사라졌으며, 봄가을에 공자에게 제사를 지내고 초하루와 보름에 향을 피운다.

의성향교는 조선 태조 3년1394에 세웠다고 전하지만 이에 대한 정확한 기록은 없다. 향교의 자리도 성종 때 고을 수령이었던 이종준에 의해 옮겨졌다고 하지만 자료가 부족해서 원래의 위치를 알 수 없다.

서로 다른 흙담을 사이에 두고 제사를 지내는 공간인 대성전이 앞에 있고 공부를 하는 공간인 명륜당은 뒤에 있어서, 전학후묘前學後廟인 일반적인 향교와 다르게 그 자리 배치가 독특하다.

"""
    },
    {
        "id": 10,
        "name": "도서동의회나무",
        "category": "nature",
        "type": "nature",
        "lat": "36.3481947101056",
        "lng": "128.696013487921",
        "description": """회나무는 잎이 지는 나무로 8월에 황백색 꽃이 피며 열매는 10월에 익는다. 회나무는 예로부터 귀하게 취급되어 집안에 심으면 행복이 찾아온다고 믿어 우리나라에서 즐겨 심었던 민속 나무이다.
의성읍 도서동의 회나무의 나이는 600년 정도로 추정하며, 높이는 18m, 둘레는 10m 정도이다. 옛날에 치질약에 좋다 하여 나무껍질을 벗겨가서 동쪽과 북서쪽에만 껍질이 남아 있다. 가지가 지상으로부터 3m 되는 지점에서 세 갈래로 갈라져 있다. 가운데 있는 가지는 말라 죽었으며, 동쪽과 서쪽에 있는 가지만 살아 있다. 나무의 밑동 부분은 썩어서 큰 구멍이 나 있는 상태이다.
1919년 조선총독부 이름으로 출판된 『조선거수노수명목지朝鮮巨樹老樹名木誌』에는 남북한을 통틀어 208건의 회화나무 중 도서동의 회나무가 가슴 높이의 둘레가 가장 크다고 적혀 있다. 또 1972년에 발간된 『보호수지保護樹誌』에 실려 있는 360건 중에서도 단연코 1위였다.
나무 아래에서는 당산제堂山祭*가 열리기도 한다.

* 당산제 : 마을의 수호신인 당산신(당산할아버지와 당산할머니)에게 마을의 평안과 풍요 등을 기원하는 지역공동체의 의식이다.
"""
    },
    {
        "id": 12,
        "name": "사촌리 향나무",
        "category": "nature",
        "type": "nature",
        "lat": "36.4242994732186",
        "lng": "128.761855430048",
        "description": """향나무는 상나무 또는 노송나무로 부르기도 하며 키는 약 20m까지 자란다. 꽃은 4월에 피며 열매는 이듬해 가을에 자줏빛을 띤 검은색으로 익고, 안에 1~6개(주로 3개)의 종자가 들어 있다. 향나무 줄기의 단단한 부분은 강한 향기를 내는데, 이것을 불에 태우면 더 진한 향기를 내므로 제사 때 향료로 널리 쓰였다.
사촌리 향나무는 의성 지역에서 고택으로 유명한 만취당 앞 골목에 심겨 있고, 나이는 500년 정도로 추정한다. 높이는 8m, 줄기의 폭은 25m 정도이다. 나무의 보존 상태가 매우 좋으며, 향나무의 줄기가 하늘로 날아오르는 모양을 하고 있다.
사촌리 향나무는 조선 연산군1494~1506 재위 때 송은松隱 김광수金光粹가 심은 것으로, 만년 동안 푸르게 살라는 의미를 붙여 만년송이라 불렀다고 전한다.
의성 사촌리 향나무는 나무가 가지는 기능과 역할에 대한 가치뿐만 아니라 선조들이 나무를 심는 마음과 자연을 사랑하는 사상도 함께 볼 수 있는 소중한 문화 자산이다.

"""
    },
    {
        "id": 13,
        "name": "제오리 공룡 발자국 화석 산지",
        "category": "nature",
        "type": "nature",
        "lat": "36.2863142167142",
        "lng": "128.695783749646",
        "description": """금성면 제오리에 있는 공룡발자국화석은 1987년 의성군 지역의 도로를 넓히기 위하여 공사를 하던 중 산허리 부분에 있는 흙을 깎아내면서 발견하였다.

제오리의 공룡 발자국은 약 1억 5천만 년 전 중생대 백악기의 것으로 추정하며, 공룡발자국화석 중 국내 최초로 천연기념물로 지정되었다.

1,656㎡(약 500평)나 되는 넓은 지역에 316개의 크고 작은 초식공룡과 육식공룡의 발자국이 함께 발견되어 이곳이 대규모 공룡의 서식지였음을 짐작할 수 있다.

발자국의 보존 상태가 양호하고 발의 생김새와 크기, 발자국의 폭, 그리고 걷는 방향을 알 수 있다
"""
    },
    {
        "id": 14,
        "name": "숲속체험마을",
        "category": "theme_park",
        "type": "theme_park",
        "lat": "36.3602423184847",
        "lng": "128.680473073208",
        "description": """여울 문화예술힐링체험마을은 음악을 사랑하고 좋아하여 취미활동 및 음악 봉사의 목적으로 시작된 여울연주단이 지역 내 음악문화 예술 보급에 기여하기 위해 설립하였으며, 음악과 문화예술체험을 매개로 삶의 질을 향상 시키고 현대인들의 편안한 휴식처가 되기 위한 곳이다."""
    },
    {
        "id": 15,
        "name": "제월 아트체험센터",
        "category": "theme_park",
        "type": "theme_park",
        "lat": "36.3635013433319",
        "lng": "128.716775260962",
        "description": "제월아트체험센터는 마을기업, 예비 사회적 기업을 거쳐 사회적 기업으로 성장한 복합문화예술단체이다."
    },
    {
        "id": 11,
        "name": "의성토종마늘마을",
        "category": "tourist_spot",
        "type": "tourist_spot",
        "lat": "36.2506373428295",
        "lng": "128.75830607346",
        "description": "마늘의 고향, 의성의 뿌리 토종마늘마을은 2004년 10월 행정자치부 지정 3차 정보화마을로 지정되었으며 현재 사미리, 효선 1.2리 세 개 마을 주민들이 정보화센터를 운영하고 있다."
    },
    {
        "id": 16,
        "name": "애플리즈",
        "category": "theme_park",
        "type": "theme_park",
        "lat": "36.437000757159",
        "lng": "128.722902834551",
        "description": """한국애플리즈는 사과와인을 생산하는 와인전문기업이다. 10여 년 동안 다양한 사과와인을 생산해 온 이곳은 와인이 만들어지는 전반적인 과정을 살펴볼 수 있을 뿐 아니라, 와인도 직접 만들어 볼 수 있다."""
    },
    {
        "id": 17,
        "name": "태양농촌체험휴양마을",
        "category": "tourist_spot",
        "type": "tourist_spot",
        "lat": "36.4258706219352",
        "lng": "128.438954368127",
        "description": "농촌 체험과 휴양을 한번에 할 수 있는 관광 명소"
    },
    {
        "id": 18,
        "name": "의성 모흥 황토마을",
        "category": "theme_park",
        "type": "theme_park",
        "lat": "36.3376882420478",
        "lng": "128.434485581306",
        "description": "모흥황토마을은 양질의 황토에서 생산되는 황토쌀과 황토사과가 유명하다. 모흥황토마을은 2003년 행정자치부 지정 2차 정보화마을로 지정되었으며 현재 모흥리 마을 주민들이 정보화센터를 운영하고 있다."
    },
    {
        "id": 19,
        "name": "교촌 농촌 체험마을",
        "category": "tourist_spot",
        "type": "tourist_spot",
        "lat": "36.3697221415746",
        "lng": "128.470518284151",
        "description": "교촌 체험 마을은 안계면 교촌리에 위치한 구 교촌 초등학교를 활용하여 만들어진 시설로서, 이용객들에게 농촌에 대해 알 수 있고 자연을 가까이 할 수 있는 기회를 제공하고 있다."
    },
    {
        "id": 20,
        "name": "산운생태공원",
        "category": "tourist_spot",
        "type": "tourist_spot",
        "lat": "36.243343828955",
        "lng": "128.702984890381",
        "description": "자연경관이 수려하고 옛 농촌의 모습을 그대로 간직하고 있는 산운마을에 생태관과 자연학습원을 조성하여 자연생태관찰과 전통문화를 체험하는 산교육장으로 활용하고 있다."
    },
    {
    "id": 41,
    "name": "의성마늘보쌈",
    "category": "restaurant",
    "type": "korean",
    "description": "의성의 특산품인 마늘을 활용한 보쌈이 유명한 곳입니다. 신선한 마늘과 함께 먹는 보쌈은 정말 맛있어요. 의성 여행 시 꼭 방문해야 할 맛집입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 42,
    "name": "의성마늘칼국수",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘의 진한 맛이 살아있는 칼국수입니다. 마늘의 매운맛과 칼국수의 고소함이 조화를 이루어 정말 맛있어요. 겨울철에 특히 인기가 많습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 43,
    "name": "의성마늘삼겹살",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘과 함께 구워먹는 삼겹살이 유명한 곳입니다. 마늘의 향과 삼겹살의 고소함이 완벽하게 어우러져서 정말 맛있어요. 가족 모임에 좋은 곳입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 44,
    "name": "의성마늘닭갈비",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 듬뿍 넣어 만드는 닭갈비가 특별합니다. 마늘의 매운맛과 닭고기의 부드러움이 조화를 이루어 정말 맛있어요. 매콤달콤한 양념이 일품입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 45,
    "name": "의성마늘순대",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 순대가 유명한 곳입니다. 마늘의 향이 가득한 순대는 정말 특별한 맛이에요. 의성 여행 시 꼭 맛봐야 할 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 46,
    "name": "의성마늘김치",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 사용해 만드는 김치가 유명한 곳입니다. 마늘의 진한 맛이 살아있는 김치는 정말 맛있어요. 밥반찬으로 최고입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 47,
    "name": "의성마늘된장찌개",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 된장찌개가 특별합니다. 마늘의 향과 된장의 고소함이 조화를 이루어 정말 맛있어요. 건강식으로도 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 48,
    "name": "의성마늘국수",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 국수가 유명한 곳입니다. 마늘의 매운맛과 국수의 쫄깃함이 조화를 이루어 정말 맛있어요. 간단한 한끼 식사로 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 49,
    "name": "의성마늘비빔밥",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 비빔밥이 특별합니다. 마늘의 향과 다양한 나물의 맛이 조화를 이루어 정말 맛있어요. 건강식으로도 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 50,
    "name": "의성마늘떡볶이",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 떡볶이가 유명한 곳입니다. 마늘의 매운맛과 떡볶이의 쫄깃함이 조화를 이루어 정말 맛있어요. 간식으로도 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 51,
    "name": "의성마늘피자",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 토핑으로 사용하는 피자가 특별합니다. 마늘의 향과 치즈의 고소함이 조화를 이루어 정말 맛있어요. 이탈리안 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 52,
    "name": "의성마늘파스타",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 넣어 만드는 파스타가 유명한 곳입니다. 마늘의 향과 파스타의 알덴테한 식감이 조화를 이루어 정말 맛있어요. 이탈리안 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 53,
    "name": "의성마늘스테이크",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 소스로 사용하는 스테이크가 특별합니다. 마늘의 향과 스테이크의 부드러움이 조화를 이루어 정말 맛있어요. 고급스러운 분위기입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 54,
    "name": "의성마늘샌드위치",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 넣어 만드는 샌드위치가 유명한 곳입니다. 마늘의 향과 신선한 채소의 맛이 조화를 이루어 정말 맛있어요. 간단한 식사로 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 55,
    "name": "의성마늘버거",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 소스로 사용하는 버거가 특별합니다. 마늘의 향과 패티의 고소함이 조화를 이루어 정말 맛있어요. 패스트푸드의 새로운 맛입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 56,
    "name": "의성마늘초밥",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 초밥이 유명한 곳입니다. 마늘의 향과 신선한 생선의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 57,
    "name": "의성마늘라멘",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 라멘이 특별합니다. 마늘의 향과 라멘의 진한 국물이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 58,
    "name": "의성마늘우동",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 우동이 유명한 곳입니다. 마늘의 향과 우동의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 59,
    "name": "의성마늘덮밥",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 덮밥이 특별합니다. 마늘의 향과 다양한 재료의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 60,
    "name": "의성마늘탕수육",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 소스로 사용하는 탕수육이 유명한 곳입니다. 마늘의 향과 탕수육의 바삭함이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 61,
    "name": "의성마늘짜장면",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 넣어 만드는 짜장면이 특별합니다. 마늘의 향과 짜장면의 진한 맛이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 62,
    "name": "의성마늘탕탕이",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 넣어 만드는 탕탕이가 유명한 곳입니다. 마늘의 향과 탕탕이의 매운맛이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 63,
    "name": "의성마늘깐풍기",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 넣어 만드는 깐풍기가 특별합니다. 마늘의 향과 깐풍기의 바삭함이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 64,
    "name": "의성마늘양꼬치",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 소스로 사용하는 양꼬치가 유명한 곳입니다. 마늘의 향과 양고기의 부드러움이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 65,
    "name": "의성마늘샤브샤브",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 소스로 사용하는 샤브샤브가 특별합니다. 마늘의 향과 신선한 재료의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 66,
    "name": "의성마늘스키야키",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 스키야키가 유명한 곳입니다. 마늘의 향과 다양한 재료의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 67,
    "name": "의성마늘오코노미야키",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 오코노미야키가 특별합니다. 마늘의 향과 오코노미야키의 고소함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 68,
    "name": "의성마늘타코야키",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 타코야키가 유명한 곳입니다. 마늘의 향과 타코야키의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 69,
    "name": "의성마늘오뎅",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 소스로 사용하는 오뎅이 특별합니다. 마늘의 향과 오뎅의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 70,
    "name": "의성마늘소바",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 소바가 유명한 곳입니다. 마늘의 향과 소바의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 21,
    "name": "카페 나인",
    "category": "cafe",
    "type": "cafe",
    "description": "분위기 좋은 카페에서 맛있는 커피를 즐길 수 있어요. 남대천 수변공원 근처에 위치해서 뷰도 좋고, 디저트도 훌륭합니다. 친구들과 수다 떨기 좋은 곳이에요.",
    "lat": 36.353355,
    "lng": 128.704797
  },
  {
    "id": 22,
    "name": "카페비야",
    "category": "cafe",
    "type": "cafe",
    "description": "조용하고 아늑한 분위기의 카페입니다. 커피 맛이 정말 좋고, 특히 아메리카노가 인기가 많아요. 공부하거나 책 읽기 좋은 분위기입니다.",
    "lat": 36.346334,
    "lng": 128.69864
  },
  {
    "id": 23,
    "name": "Angel-in-us",
    "category": "cafe",
    "type": "cafe",
    "description": "체인점이지만 의성에서 가장 깔끔하고 맛있는 커피를 제공해요. 시즌 메뉴도 다양하고, 특히 스무디류가 인기가 많습니다.",
    "lat": 36.352218,
    "lng": 128.69663
  },
  {
    "id": 24,
    "name": "카페5번가",
    "category": "cafe",
    "type": "cafe",
    "description": "안계면에 위치한 카페로, 승마장과 탁 트인 시골 뷰를 자랑합니다. 경북 뷰 카페 100선에 선정된 곳으로, 사진 찍기 좋은 곳이에요.",
    "lat": 36.360296,
    "lng": 128.691872
  },
  {
    "id": 25,
    "name": "커피에반하다 의성점",
    "category": "cafe",
    "type": "cafe",
    "description": "커피에반하다 체인점으로, 일관된 맛과 품질을 보장합니다. 의성에서도 서울 못지않은 커피를 즐길 수 있어요.",
    "lat": 36.362482,
    "lng": 128.701539
  },
  {
    "id": 26,
    "name": "서림카페",
    "category": "cafe",
    "type": "cafe",
    "description": "점곡면에 위치한 작은 카페입니다. 마을 분위기가 그대로 느껴지는 아늑한 곳이에요. 커피도 맛있고 주인분도 친절합니다.",
    "lat": 36.361803,
    "lng": 128.704341
  },
  {
    "id": 27,
    "name": "체리코나",
    "category": "cafe",
    "type": "cafe",
    "description": "단밀면에 위치한 카페로, 체리 관련 메뉴가 특별합니다. 계절에 따라 다른 맛을 즐길 수 있고, 특히 체리 라떼가 인기가 많아요.",
    "lat": 36.362566,
    "lng": 128.687488
  },
  {
    "id": 28,
    "name": "Hyangchondang",
    "category": "cafe",
    "type": "cafe",
    "description": "전통시장 근처에 위치한 카페로, 향촌당이라는 이름답게 전통적인 분위기가 느껴집니다. 한옥 스타일의 인테리어가 매력적이에요.",
    "lat": 36.359383,
    "lng": 128.70464
  },
  {
    "id": 29,
    "name": "가로숲카페",
    "category": "cafe",
    "type": "cafe",
    "description": "점곡면에 위치한 숲속 카페입니다. 자연 속에서 커피를 즐길 수 있어서 힐링하기 좋은 곳이에요. 특히 가을 단풍철이 아름답습니다.",
    "lat": 36.358475,
    "lng": 128.703615
  },
  {
    "id": 30,
    "name": "해피데이 흑마늘카페",
    "category": "cafe",
    "type": "cafe",
    "description": "봉양면에 위치한 특별한 카페로, 흑마늘을 활용한 메뉴가 특별합니다. 건강에 좋은 흑마늘 커피와 디저트를 즐길 수 있어요.",
    "lat": 36.346631,
    "lng": 128.70054
  },
  {
    "id": 31,
    "name": "꽃이 숲을 이루다",
    "category": "cafe",
    "type": "cafe",
    "description": "의성군 카페맛집 1위로 선정된 곳입니다. 꽃과 자연을 테마로 한 아름다운 카페로, 인스타그램에서 인기가 많은 곳이에요.",
    "lat": 36.361598,
    "lng": 128.688737
  },
  {
    "id": 32,
    "name": "스윗띵",
    "category": "cafe",
    "type": "cafe",
    "description": "의성군 카페맛집 3위로 선정된 곳입니다. 달콤한 디저트가 특별하고, 특히 케이크류가 인기가 많아요. 커피와 함께 즐기기 좋습니다.",
    "lat": 36.343654,
    "lng": 128.702392
  },
  {
    "id": 33,
    "name": "논밭에",
    "category": "cafe",
    "type": "cafe",
    "description": "안계면에 위치한 카페로, 넓은 안계평야 들판 뷰를 자랑합니다. 경북 뷰 카페 100선에 선정된 곳으로, 사진 찍기 좋은 곳이에요.",
    "lat": 36.360497,
    "lng": 128.688227
  },
  {
    "id": 34,
    "name": "아이리스카페",
    "category": "cafe",
    "type": "cafe",
    "description": "의성군에서 인기가 많은 카페입니다. 아이리스라는 이름답게 꽃을 테마로 한 아름다운 인테리어가 특징이에요.",
    "lat": 36.358728,
    "lng": 128.699696
  },
  {
    "id": 35,
    "name": "민속떡집",
    "category": "cafe",
    "type": "cafe",
    "description": "전통 떡을 테마로 한 카페입니다. 현대적인 카페 분위기에서 전통 떡을 즐길 수 있어서 특별한 경험을 할 수 있어요.",
    "lat": 36.360285,
    "lng": 128.688333
  },
  {
    "id": 36,
    "name": "카카베이커리카페",
    "category": "cafe",
    "type": "cafe",
    "description": "베이커리와 카페가 결합된 곳입니다. 신선한 빵과 커피를 함께 즐길 수 있어서 아침 식사나 오후 간식으로 좋아요.",
    "lat": 36.354663,
    "lng": 128.701576
  },
  {
    "id": 37,
    "name": "미라보양과자점",
    "category": "cafe",
    "type": "cafe",
    "description": "양과자점이지만 카페 메뉴도 제공하는 곳입니다. 맛있는 케이크와 커피를 함께 즐길 수 있어서 디저트 타임에 인기가 많아요.",
    "lat": 36.348288,
    "lng": 128.69063
  },
  {
    "id": 38,
    "name": "헬로 키티 카페",
    "category": "cafe",
    "type": "cafe",
    "description": "헬로 키티를 테마로 한 귀여운 카페입니다. 아이들과 함께 가기 좋은 곳이고, 키티 팬들에게는 필수 방문지예요.",
    "lat": 36.352348,
    "lng": 128.705575
  },
  {
    "id": 39,
    "name": "1987양반댁",
    "category": "cafe",
    "type": "cafe",
    "description": "전통적인 양반댁을 테마로 한 카페입니다. 한옥 분위기에서 현대적인 커피를 즐길 수 있어서 특별한 경험을 할 수 있어요.",
    "lat": 36.352244,
    "lng": 128.706508
  },
  {
    "id": 40,
    "name": "오늘살롱",
    "category": "cafe",
    "type": "cafe",
    "description": "살롱 분위기의 카페입니다. 아늑하고 세련된 분위기에서 커피를 즐길 수 있어서 데이트 장소로도 인기가 많아요.",
    "lat": 36.355718,
    "lng": 128.687274
  }
]


# 인덱스 생성
def create_index():
    index_name = "uiseong_attractions_en"
    
    if es.indices.exists(index=index_name):
        print(f"인덱스 '{index_name}'가 이미 존재합니다.")
        return index_name

    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "text", "analyzer": "standard"},
                "category": {"type": "keyword"},
                "type": {"type": "keyword"},
                "lat": {"type": "float"},
                "lng": {"type": "float"},
                "description": {"type": "text", "analyzer": "standard"},
                "content_vector": {
                    "type": "dense_vector",
                    "dims": 384  # MiniLM의 출력 차원
                },
                "created_at": {"type": "date"}
            }
        }
    }

    es.indices.create(index=index_name, body=mapping)
    print(f"✅ 인덱스 '{index_name}' 생성 완료")
    return index_name

# 데이터 업로드
def upload_data(index_name):
    success_count = 0
    error_count = 0

    for attraction in UISEONG_ATTRACTIONS:
        try:
            doc_id = attraction['id']
            embedding = get_embedding_from_description(attraction['description'])

            upload_body = {
                "id": doc_id,
                "name": attraction['name'],
                "category": attraction['category'],
                "type": attraction['category'],
                "lat": float(attraction['lat']) if attraction['lat'] else None,
                "lng": float(attraction['lng']) if attraction['lng'] else None,
                "description": attraction['description'],
                "content_vector": embedding,
                "created_at": datetime.utcnow()
            }

            response = es.index(index=index_name, id=doc_id, body=upload_body)
            if response['result'] in ['created', 'updated']:
                print(f"✅ {attraction['name']} 업로드 성공")
                success_count += 1
            else:
                print(f"❌ {attraction['name']} 업로드 실패")
                error_count += 1

        except Exception as e:
            print(f"❌ {attraction['name']} 업로드 중 오류: {e}")
            error_count += 1

    print(f"\n📊 업로드 결과: 성공 {success_count}개, 실패 {error_count}개")

# 벡터 검색
def vector_search(index_name, query_text, category):
    print(f"\n🔍 벡터 기반 검색 (category = '{category}'):")

    query_vector = get_embedding_from_description(query_text)

    search_query = {
        "query": {
            "bool": {
                "must": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'content_vector') + 0.1",
                            "params": {"query_vector": query_vector}
                        }
                    }
                },
                "filter": [
                    {
                        "term": {"category": category}
                    }
                ]
            }
        },
        "size": 5
    }

    response = es.search(index=index_name, body=search_query)
    print(f"검색 결과 {len(response['hits']['hits'])}건:")
    for hit in response["hits"]["hits"]:
        score = hit["_score"]
        source = hit["_source"]
        print(f"  🔹 {source['name']} (score: {score:.4f})")

# 메인 함수
def main():
    print("🚀 Elasticsearch에 의성군 관광지 데이터를 업로드합니다...")

    if not es.ping():
        print("❌ Elasticsearch 연결 실패: 9200 포트 확인 필요")
        return

    print("✅ Elasticsearch 연결 성공")
    index_name = create_index()
    upload_data(index_name)

    test_text = "학문을 닦던 조선시대 서재"
    vector_search(index_name, test_text, category="cultural_heritage")

    print("\n🎉 모든 작업 완료!")

if __name__ == "__main__":
    main()