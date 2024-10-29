import math
import random


def generate_balance_emoticon(balance):
    items = ["🍦", "🍔", "🍓", "🍩", "🍕", "🍪", "🍫", "🎃"]
    item_count = max(1, int(math.log10(balance)))
    generated_items = "".join(random.choice(items) for _ in range(item_count))
    return f"(:３  {generated_items}  っ)∋"
