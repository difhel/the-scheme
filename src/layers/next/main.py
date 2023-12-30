"""
Main module with test realization of the scheme
"""
from core.builtins import BSType, BSParam, BSStr, BSInt, BSNull
user = BSType(
    "User", [
        BSParam("id", BSInt),
        BSParam("first_name", BSStr)
    ],
    "user"
)


bot = BSType(
    "User", [
        BSParam("id", BSInt),
        BSParam("first_name", BSStr | BSNull),
        BSParam("bot_creator", user)
    ],
    "bot"
)

# BSInt.to_BS_object("crash!")

# x = BSInt.to_BS_object(42)
# print(x)
# BSNull.to_BS_object(None)
# print(user.convert_to_scheme())
# print(bot.convert_to_scheme())

print(bot.convert_to_scheme())

user_data = {
    "id": 42,
    "first_name": "Mark"
}
user_obj = user.to_BS_object(user_data)

bot_obj = bot.to_BS_object({
    "id": 1,
    "first_name": None,
    "bot_creator": user_obj
})
