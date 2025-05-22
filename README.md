# unstructured-renamer

Sebuah alat untuk mengganti nama file dalam folder menjadi format tertentu, menambahkan nomor urut, dan menghasilkan log CSV.

## Ikhtisar

Utilitas ini membantu Anda mengorganisir file dengan mengganti nama sesuai dengan pola yang telah ditentukan dan menjaga catatan semua perubahan dalam format CSV untuk pelacakan dan pengelolaan yang mudah.

## Fitur

- Mengganti nama file menggunakan pola yang dapat disesuaikan
- Menambahkan penomoran berurutan pada nama file
- Menghasilkan log CSV yang detail untuk semua operasi file
- Dukungan untuk pemrosesan batch dari beberapa file
- Antarmuka yang sederhana dan intuitif

## Instalasi

```
git clone https://github.com/kloworizer/unstructured-renamer.git
cd unstructured-renamer
# Ikuti petunjuk pengaturan
```

## Penggunaan

Contoh dasar:

```
unstructured-renamer --folder /path/to/files --pattern "document_{seq}" --start 1
```

Untuk petunjuk penggunaan yang lebih detail, lihat [dokumentasi](docs/usage.md).

## Rilis Terbaru

Versi stabil terbaru tersedia di halaman [Rilis](https://github.com/kloworizer/unstructured-renamer/releases).

## Lisensi

[MIT](LICENSE)