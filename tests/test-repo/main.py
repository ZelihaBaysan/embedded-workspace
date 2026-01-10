def main():
    questions = [
        "1. Daryl Dixson'un mesleği neydi kıyamet öncesi?",
        "2. Daryl Dixson oynayan aktör kimdir?",
        "3. Daryl Dixson'un favori silahı nedir?",
        "4. Daryl Dixson'un hobileri nelerdir?",
        "5. Daryl Dixson'ın deri yeleğinin arkasında ne motifi vardır?"
    ]

    answers = [
        "Merle ile dolanıyorlardı",
        "Norman Reedus",
        "Crossbow",
        "Motor sürmek",
        "Kanat"
    ]

    print("Daryl Dixson hakkında 5 soruya ait cevapları görmek için 1-5 arasında bir sayı girin.")
    print("Çıkmak için 'exit' yazın.")

    while True:
        choice = input("Soru numarası (1-5) veya exit: ").strip()
        if choice.lower() == "exit":
            print("Programdan çıkılıyor...")
            break
        elif choice in ["1", "2", "3", "4", "5"]:
            idx = int(choice) - 1
            print(f"{questions[idx]} \nCevap: {answers[idx]}\n")
        else:
            print("Lütfen 1-5 arası bir sayı veya 'exit' yazın.")


if __name__ == "__main__":
    main()
