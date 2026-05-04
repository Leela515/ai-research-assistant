from app.services.answer_service import AnswerService

service = AnswerService()

response = service.answer_question(
    "What are the training methods used in spiking neural networks?"
)

print("FINAL ANSWER:")
print(response["answer"])

print("\nDRAFT ANSWER:")
print(response["draft_answer"])

print("\nCONFIDENCE:")
print(response["confidence"])

print("\nCRITIC:")
print(response["critic_review"])

print("\nSOURCES:")
for source in response["sources"]:
    print(source["title"], source["section_title"], source["score"])