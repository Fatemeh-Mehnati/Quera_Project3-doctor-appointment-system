# فهرست مسیرها

همه مسیرهای پروژه و کاری که هرکدام انجام می‌دهند.

**مسئول تکمیل:** سام (WP14) — با کمک عرفان در WP9

**ستون دسترسی:** عمومی = بدون نیاز به ورود | کاربر = نیازمند لاگین | ادمین = فقط کارکنان

---

## accounts

| مسیر | نام | متد | ویو | دسترسی | توضیح |
|---|---|---|---|---|---|
| `/accounts/register/` | `register` | GET, POST | | عمومی | فرم ثبت‌نام کاربر جدید |
| `/accounts/login/` | `login` | GET, POST | | عمومی | ورود با ایمیل و رمز |
| `/accounts/otp/request/` | `otp_request` | GET, POST | | عمومی | درخواست کد یک‌بارمصرف با ایمیل |
| `/accounts/otp/verify/` | `otp_verify` | GET, POST | | عمومی | تایید کد و ورود |
| `/accounts/logout/` | `logout` | POST | | کاربر | خروج از حساب |
| `/accounts/profile/` | `profile` | GET | | کاربر | مشاهده پروفایل |
| `/accounts/wallet/` | `wallet` | GET | | کاربر | موجودی کیف پول |
| `/accounts/wallet/charge/` | `wallet_charge` | GET, POST | | کاربر | شارژ کیف پول |
| `/accounts/wallet/transactions/` | `wallet_transactions` | GET | | کاربر | تاریخچه تراکنش‌ها |

<!-- TODO: بعد از WP4 و WP7 با مسیرهای واقعی تطبیق داده شود -->

---

## doctors

| مسیر | نام | متد | ویو | دسترسی | توضیح |
|---|---|---|---|---|---|
| `/doctors/` | `doctor_list` | GET | | عمومی | لیست پزشکان با صفحه‌بندی |
| `/doctors/search/` | `doctor_search` | GET | | عمومی | جستجو بر اساس نام یا تخصص |
| `/doctors/<int:pk>/` | `doctor_detail` | GET | | عمومی | جزئیات پزشک، بازه‌های خالی، نظرات |
| `/doctors/<int:pk>/review/` | `review_create` | GET, POST | | کاربر | ثبت نظر و امتیاز |

<!-- TODO: بعد از WP5 و WP8 تکمیل شود -->

---

## appointments

| مسیر | نام | متد | ویو | دسترسی | توضیح |
|---|---|---|---|---|---|
| `/appointments/book/<int:slot_id>/` | `appointment_book` | GET, POST | | کاربر | رزرو یک بازه زمانی |
| `/appointments/my/` | `appointment_list` | GET | | کاربر | نوبت‌های کاربر |
| `/appointments/<int:pk>/cancel/` | `appointment_cancel` | POST | | کاربر | لغو نوبت و بازگشت وجه |

<!-- TODO: بعد از WP6 تکمیل شود -->

---

## سایر

| مسیر | نام | متد | دسترسی | توضیح |
|---|---|---|---|---|
| `/` | `home` | GET | عمومی | صفحه اصلی |
| `/admin/` | — | GET, POST | ادمین | پنل مدیریت جنگو |

---

## یادداشت

<!-- TODO: هر مسیری که در پیاده‌سازی اضافه یا حذف شد اینجا ثبت شود -->
