import requests
import pytest

@pytest.fixture(scope="module")
def superheroes_api():
    response = requests.get('https://akabab.github.io/superhero-api/api/all.json')
    response.raise_for_status()
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    return data

def has_real_work(hero):
    work = hero.get('work', {}).get('occupation', "").strip()
    return work and work != "-"

def filter_heroes(heroes, gender=None, has_work=None):
    filtered = []
    for hero in heroes:
        hero_gender = hero.get('appearance', {}).get('gender', "").lower()
        hero_work = has_real_work(hero)  # Используем новую функцию
        height_str = hero.get('appearance', {}).get('height', [None, None])[1]

        if ((gender is None or hero_gender == gender.lower()) and
                (has_work is None or hero_work == has_work) and
                isinstance(height_str, str) and
                height_str.replace(" cm", "").isdigit()):
            filtered.append(hero)
    return filtered


def print_hero_info(hero, category):
    print(f"\nСамый высокий герой ({category}):")
    print(f"Имя: {hero['name']}")
    print(f"Рост: {hero['appearance']['height'][1]}")
    print(f"Пол: {hero['appearance']['gender']}")
    print(f"Работа: {hero.get('work', {}).get('occupation', 'не указана')}")

@pytest.mark.parametrize("gender,has_work", [
    ("Male", True),
    ("Female", True),
    ("Male", False),
    ("Female", False)
])
def test_tallest_by_gender_and_work(superheroes_api, gender, has_work):
    filtered = filter_heroes(superheroes_api, gender, has_work)

    if not filtered:
        pytest.skip(f"Нет героев с параметрами: gender={gender}, work={has_work}")

    tallest = max(filtered, key=lambda h: int(h['appearance']['height'][1].replace(" cm", "")))
    print_hero_info(tallest, f"пол={gender}, работа={'есть' if has_work else 'нет'}")

    assert tallest['appearance']['gender'].lower() == gender.lower()
    assert has_real_work(tallest) == has_work


def test_tallest_male_with_work(superheroes_api):
    filtered = filter_heroes(superheroes_api, "male", True)
    assert filtered, "Не найдено мужчин с работой"

    tallest = max(filtered, key=lambda h: int(h['appearance']['height'][1].replace(" cm", "")))
    print_hero_info(tallest, "мужчины с работой")

    assert tallest['appearance']['gender'].lower() == "male"
    assert has_real_work(tallest)
    assert "name" in tallest
    assert "height" in tallest['appearance']


def test_tallest_female_with_work(superheroes_api):
    filtered = filter_heroes(superheroes_api, "female", True)
    assert filtered, "Не найдено женщин с работой"

    tallest = max(filtered, key=lambda h: int(h['appearance']['height'][1].replace(" cm", "")))
    print_hero_info(tallest, "женщины с работой")

    assert tallest['appearance']['gender'].lower() == "female"
    assert has_real_work(tallest)
    assert "name" in tallest
    assert "height" in tallest['appearance']


def test_tallest_male_without_work(superheroes_api):
    filtered = filter_heroes(superheroes_api, "male", False)
    assert filtered, "Не найдено мужчин без работы"

    tallest = max(filtered, key=lambda h: int(h['appearance']['height'][1].replace(" cm", "")))
    print_hero_info(tallest, "мужчины без работы")

    assert tallest['appearance']['gender'].lower() == "male"
    assert not has_real_work(tallest)
    assert "name" in tallest
    assert "height" in tallest['appearance']


def test_tallest_female_without_work(superheroes_api):
    filtered = filter_heroes(superheroes_api, "female", False)
    assert filtered, "Не найдено женщин без работы"

    tallest = max(filtered, key=lambda h: int(h['appearance']['height'][1].replace(" cm", "")))
    print_hero_info(tallest, "женщины без работы")

    assert tallest['appearance']['gender'].lower() == "female"
    assert not has_real_work(tallest)
    assert "name" in tallest
    assert "height" in tallest['appearance']


def test_no_hero_case(superheroes_api):
    filtered = filter_heroes(superheroes_api, "other", False)
    print("\nТест для несуществующей комбинации: пол=other, работа=нет")
    print("Найдено героев:", len(filtered))
    assert not filtered, "Найдены герои, хотя не должны были"


def test_tallest_overall(superheroes_api):
    all_heroes = filter_heroes(superheroes_api)
    tallest = max(all_heroes, key=lambda h: int(h['appearance']['height'][1].replace(" cm", "")))
    print_hero_info(tallest, "среди всех героев")
    assert "name" in tallest
    assert "height" in tallest['appearance']