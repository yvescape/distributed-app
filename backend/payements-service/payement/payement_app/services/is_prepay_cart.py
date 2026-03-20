# def is_prepaid_card(card_number):

#     # retirer les espaces
#     card_number = card_number.replace(" ", "")

#     # vérification simple
#     if len(card_number) == 16:
#         return True

#     return False

#     if is_prepaid_card(card_number):
#         payment.status = "success"
#         update_order_status(payment.order_id, "confirmed")
#     else:
#         payment.status = "failed"
#         update_order_status(payment.order_id, "cancelled")

#     payment.save()