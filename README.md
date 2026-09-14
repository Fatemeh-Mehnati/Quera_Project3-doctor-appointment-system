# 🩺 سیستم نوبت‌دهی آنلاین پزشکان

یک سامانه وب برای **جستجوی پزشکان، مشاهده زمان‌های آزاد، رزرو نوبت، پرداخت هزینه ویزیت، دریافت تأییدیه ایمیل و ثبت نظر و امتیاز پزشکان**.

این پروژه به عنوان **پروژه سوم بوت‌کمپ کوئرا** توسعه داده شده و با استفاده از **Python و Django** و معماری **MVT** پیاده‌سازی شده است.

---

## ✨ امکانات

### 👤 احراز هویت و کاربران

* ثبت‌نام و ورود با ایمیل
* احراز هویت با کد یک‌بارمصرف (OTP)
* مدیریت حساب کاربری
* مدیریت کیف پول و تراکنش‌ها

### 👨‍⚕️ پزشکان

* مشاهده لیست پزشکان
* جستجوی پزشک بر اساس:

  * نام پزشک
  * تخصص
* مشاهده اطلاعات و تخصص پزشک
* مشاهده بازه‌های زمانی آزاد
* مشاهده امتیاز و نظرات کاربران

### 📅 نوبت‌دهی

* مشاهده زمان‌های خالی پزشکان
* رزرو نوبت
* جلوگیری از رزرو بازه‌های قبلاً رزروشده
* پرداخت هزینه ویزیت از کیف پول
* مشاهده وضعیت و اطلاعات نوبت

### 💳 پرداخت و کیف پول

* مدیریت موجودی کیف پول
* پرداخت هزینه ویزیت هنگام رزرو
* ثبت تراکنش‌های مالی

### 📧 ایمیل

* ارسال کد OTP
* ارسال ایمیل تأیید رزرو نوبت

### ⭐ نظرات و امتیازدهی

* امکان ثبت نظر برای پزشک
* امکان ثبت امتیاز
* ثبت نظر پس از انجام ویزیت

### 🛠 پنل مدیریت

مدیر سیستم می‌تواند موارد زیر را مدیریت کند:

* پزشکان
* تخصص‌ها
* بازه‌های زمانی
* هزینه ویزیت
* کاربران
* نوبت‌ها

---

## 🧰 تکنولوژی‌های استفاده‌شده

| تکنولوژی       | کاربرد                  |
| -------------- | ----------------------- |
| Python 3.13    | زبان برنامه‌نویسی       |
| Django         | Backend Framework       |
| SQLite         | دیتابیس محیط توسعه      |
| PostgreSQL     | دیتابیس محیط Production |
| Gunicorn       | WSGI Server             |
| Docker         | Containerization        |
| Docker Compose | مدیریت سرویس‌ها         |
| HTML / CSS     | رابط کاربری             |
| Git / GitHub   | کنترل نسخه              |

---

## 🏗 معماری پروژه

پروژه با معماری **MVT (Model-View-Template)** در Django توسعه داده شده است.

```text
Quera_Project3-doctor-appointment-system/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
│
├── appointments/
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── doctors/
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
├── documents/
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

### ساختار اپلیکیشن‌ها

**accounts**

مدیریت کاربران، احراز هویت، OTP، کیف پول و تراکنش‌ها.

**doctors**

مدیریت پزشکان، تخصص‌ها، جستجوی پزشک، نظرات و امتیازها.

**appointments**

مدیریت بازه‌های زمانی، رزرو نوبت، پرداخت و ارسال ایمیل تأییدیه.

---

## 🚀 راه‌اندازی پروژه

### 1. Clone کردن پروژه

```bash
git clone https://github.com/Fatemeh-Mehnati/Quera_Project3-doctor-appointment-system.git
cd Quera_Project3-doctor-appointment-system
```

### 2. ساخت Virtual Environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 4. تنظیم Environment Variables

فایل نمونه `.env.example` را کپی کنید:

```bash
cp .env.example .env
```

سپس فایل `.env` را متناسب با محیط خود تنظیم کنید.

نمونه:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
OTP_EXPIRY_SECONDS=120
```

برای محیط Production می‌توان از PostgreSQL استفاده کرد.

---

## 🗄️ اجرای Migration

```bash
python manage.py migrate
```

---

## 👨‍💼 ساخت Superuser

برای دسترسی به پنل مدیریت:

```bash
python manage.py createsuperuser
```

---

## ▶️ اجرای پروژه

```bash
python manage.py runserver
```

سپس پروژه از طریق آدرس زیر قابل دسترسی است:

```text
http://127.0.0.1:8000/
```

پنل مدیریت Django:

```text
http://127.0.0.1:8000/admin/
```

---

## 🐳 اجرای پروژه با Docker

در صورتی که Docker و Docker Compose نصب شده باشد:

```bash
docker compose up --build
```

---

## 🌱 داده‌های نمونه

برای بارگذاری داده‌های نمونه:

```bash
python manage.py loaddata fixtures/sample_data.json
```

---

## 🧪 تست پروژه

اجرای تمام تست‌ها:

```bash
python manage.py test
```

اجرای تست‌های یک اپلیکیشن خاص:

```bash
python manage.py test accounts
```

---

## 📚 مستندات

مستندات تکمیلی پروژه در پوشه `documents/` قرار گرفته‌اند.

| فایل                    | توضیحات                             |
| ----------------------- | ----------------------------------- |
| `ERD.png`               | نمودار Entity Relationship Database |
| `erd-notes.md`          | توضیحات و تصمیمات طراحی دیتابیس     |
| `api-routes.md`         | لیست Routeهای پروژه                 |
| `manual-test-report.md` | گزارش تست دستی سناریوها             |

---

## 🔐 متغیرهای محیطی

مهم‌ترین متغیرهای مورد استفاده در پروژه:

| Variable              | Description                  |
| --------------------- | ---------------------------- |
| `SECRET_KEY`          | کلید امنیتی Django           |
| `DEBUG`               | فعال/غیرفعال بودن حالت Debug |
| `ALLOWED_HOSTS`       | دامنه‌های مجاز               |
| `DB_ENGINE`           | Database Engine              |
| `DB_NAME`             | نام دیتابیس                  |
| `DB_USER`             | نام کاربر دیتابیس            |
| `DB_PASSWORD`         | رمز عبور دیتابیس             |
| `DB_HOST`             | آدرس دیتابیس                 |
| `DB_PORT`             | پورت دیتابیس                 |
| `EMAIL_BACKEND`       | Backend ارسال ایمیل          |
| `EMAIL_HOST`          | SMTP Server                  |
| `EMAIL_PORT`          | SMTP Port                    |
| `EMAIL_HOST_USER`     | ایمیل ارسال‌کننده            |
| `EMAIL_HOST_PASSWORD` | رمز/کلید ایمیل               |
| `OTP_EXPIRY_SECONDS`  | مدت اعتبار OTP               |

> ⚠️ اطلاعات حساس مانند `SECRET_KEY`، رمز دیتابیس و اطلاعات SMTP نباید مستقیماً داخل Git قرار بگیرند.

---

## 🔄 Git Workflow

پروژه با دو Branch اصلی توسعه داده شده است:

```text
main
  │
  └── نسخه نهایی پروژه

dev
  │
  └── Branch اصلی توسعه
```

برای توسعه یک Feature جدید:

```bash
git checkout dev
git pull

git checkout -b feature/<feature-name>

# development

git add .
git commit -m "Add <feature-name>"

git push -u origin feature/<feature-name>
```

سپس یک Pull Request به `dev` ایجاد می‌شود.

---

## 👥 اعضای تیم

| عضو         | مسئولیت                                                  |
| ----------- | -------------------------------------------------------- |
| فاطمه محنتی | مدیریت پروژه، Viewهای پزشک و جستجو، Template پایه، ارائه |
| علی         | مدل‌ها، فرم‌ها، منطق رزرو، Docker                        |
| عرفان       | مدل‌های کاربر، احراز هویت، OTP و تست خودکار              |
| مهیار       | کیف پول، پرداخت، لیست نوبت‌ها و تست دستی                 |
| سام         | نظرات، امتیازدهی، Template صفحات و مستندسازی             |

---

## 🎯 هدف پروژه

هدف این پروژه ایجاد یک سیستم یکپارچه برای **مدیریت فرآیند نوبت‌دهی پزشکان** است؛ به‌گونه‌ای که کاربر بتواند پزشک موردنظر خود را پیدا کند، زمان آزاد او را مشاهده کند، نوبت رزرو کند و هزینه ویزیت را از طریق کیف پول پرداخت نماید.

این پروژه همچنین تجربه عملی کار با **Django، طراحی مدل‌های دیتابیس، احراز هویت OTP، مدیریت تراکنش‌ها، ارسال ایمیل، Docker و Git Workflow تیمی** را فراهم می‌کند.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👩‍💻 Author

**Fatemeh Mehnati**

GitHub:
https://github.com/Fatemeh-Mehnati
