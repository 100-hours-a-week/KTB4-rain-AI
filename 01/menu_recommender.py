print("=== 오늘의 메뉴 추천 프로그램 ===")

name = input("이름을 입력하세요: ")
food_type = input("먹고 싶은 종류를 입력하세요 (한식/중식/일식/양식): ")
hunger = input("배고픈 정도를 입력하세요 (조금/보통/많이): ")

print()
print(f"{name}님을 위한 메뉴 추천 결과입니다!")

if food_type == "한식":
    if hunger == "많이":
        menu = "제육덮밥"
    elif hunger == "보통":
        menu = "김치찌개"
    else:
        menu = "김밥"

elif food_type == "중식":
    if hunger == "많이":
        menu = "짜장면 곱빼기"
    elif hunger == "보통":
        menu = "짬뽕"
    else:
        menu = "군만두"

elif food_type == "일식":
    if hunger == "많이":
        menu = "돈카츠"
    elif hunger == "보통":
        menu = "라멘"
    else:
        menu = "유부초밥"

else:
    menu = "편의점 도시락"

print("추천 메뉴:", menu)