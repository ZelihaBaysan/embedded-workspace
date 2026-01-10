import redis
from faker import Faker
import random
from datetime import datetime
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()

class RedisDataGenerator:
    def __init__(self):
        self.fake = Faker('tr_TR')
        self.redis = self._connect_redis()
        
    def _connect_redis(self):
        """Upstash Redis bağlantısını kurar"""
        return redis.Redis(
            host=os.getenv('UPSTASH_REDIS_HOST'),
            port=int(os.getenv('UPSTASH_REDIS_PORT')),
            password=os.getenv('UPSTASH_REDIS_PASSWORD'),
            ssl=True,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=5
        )
    
    def _generate_users(self, count=10):
        """Kullanıcı profilleri oluşturur"""
        for i in range(1, count+1):
            yield (
                f"user:{i}:profile",
                {
                    "name": self.fake.name(),
                    "email": self.fake.email(),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": random.choice(["active", "inactive", "banned"])
                }
            )
    
    def _generate_chats(self, count=5):
        """Sohbet verileri oluşturur"""
        for i in range(1, count+1):
            participants = random.sample(range(1, 11), random.randint(2, 5))
            yield (
                f"chat:{i}:metadata",
                {
                    "participants": json.dumps(participants),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message_count": random.randint(5, 50)
                }
            )
            
            # Sohbet mesajları
            messages = [
                {"sender": random.choice(participants), 
                 "text": self.fake.sentence(),
                 "timestamp": str(int(time.time()) - random.randint(0, 86400))}
                for _ in range(random.randint(5, 15))
            ]
            self.redis.lpush(f"chat:{i}:messages", *[json.dumps(m) for m in messages])

    def _generate_system_data(self):
        """Sistem verileri oluşturur (exclude edilecek)"""
        systems = [
            ("cache:user:session:1", json.dumps({"token": self.fake.sha256()})),
            ("temp:upload:123", "partial_upload"),
            ("system:health:redis", json.dumps({"memory": "1.2GB", "cpu": "45%"})),
            ("lock:message:send", "locked"),
            ("queue:email:pending", json.dumps(["welcome@example.com", "reset@example.com"]))
        ]
        for key, value in systems:
            self.redis.set(key, value)
            if key.startswith(("cache:", "temp:")):
                self.redis.expire(key, random.randint(300, 3600))

    def run(self):
        """Tüm veri üretim işlemlerini çalıştırır"""
        print("🔄 Veri üretimi başlıyor...")
        
        # Users
        for key, value in self._generate_users():
            self.redis.hset(key, mapping=value)
        
        # Chats
        self._generate_chats()
        
        # System Data
        self._generate_system_data()
        
        # Özel veri tipleri
        self.redis.sadd("tags:popular", *self.fake.words(10))
        self.redis.zadd("leaderboard", {"user1": 100, "user2": 85, "user3": 72})
        
        print("✅ Veri üretimi tamamlandı!")
        print(f"Toplam anahtar sayısı: {len(self.redis.keys('*'))}")

if __name__ == "__main__":
    generator = RedisDataGenerator()
    generator.run()