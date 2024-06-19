#include <iostream>
using namespace std;

void tampilkanMenu() {
    cout << "========================================================================\n";
    cout << "                       SELAMAT DATANG DI PROGRAM KAMI                   \n";
    cout << "                        PROGRAM PENGINGAT KESEHATAN                     \n";
    cout << "========================================================================\n";

    cout << "1. Cek tekanan darah\n";
    cout << "2. Hitung kalori\n";
    cout << "3. Cek berat badan\n";
    cout << "4. Keluar\n";
}

void tanyaLanjut() {
    char jawaban;
    cout << "\nApakah Anda ingin melanjutkan? (y/t) : ";
    cin >> jawaban;

    if (jawaban != 'y' && jawaban != 'Y') {
        cout << "Terima kasih telah cek kesehatan di program kami, semoga membantu dan sampai jumpa lagi :)";
        exit(0);
    }
}

int main() {

    float tinggi, beratIdeal;
    string jenisMakanan;
    double jumlahMakanan, kaloriPerSatuan, totalKalori;
    int pilihan, sistolik, diastolik;
    string kategoriTekananDarah[] = {"Tekanan darah rendah", "Tekanan darah normal", "Tekanan darah tinggi"};

    do {

        tampilkanMenu();

        cout << "\nMasukkan pilihan Anda : ";
        cin >> pilihan;

        switch (pilihan) {

        case 1:
            cout << "\n=====ANDA MEMILIH UNTUK CEK TEKANAN DARAH=====\n";

            cout << "\nMasukkan nilai tekanan darah sistolik (atas) : ";
            cin >> sistolik;

            cout << "Masukkan nilai tekanan darah diastolik (bawah) : ";
            cin >> diastolik;

            if (sistolik < 90 && diastolik < 60) {
                cout << kategoriTekananDarah[0] << "\n";
            } else if ((sistolik >= 90 && sistolik <= 120) && (diastolik >= 60 && diastolik <= 80)) {
                cout << kategoriTekananDarah[1] << "\n";
            } else if ((sistolik > 120) || (diastolik > 80)) {
                cout << kategoriTekananDarah[2] << "\n";
            } else {
                cout << "\nMasukkan nilai tekanan darah yang valid\n";
            }

            break;

        case 2:
            cout << "\n===============ANDA MEMILIH UNTUK MENGHITUNG KALORI===============\n";
            cout << "\nMasukkan jenis makanan : ";
            cin >> jenisMakanan;

            cout << "Masukkan jumlah " << jenisMakanan << " (dalam satuan yang sesuai) : ";
            cin >> jumlahMakanan;

            cout << "Masukkan jumlah kalori per satuan " << jenisMakanan << " : ";
            cin >> kaloriPerSatuan;

            totalKalori = jumlahMakanan * kaloriPerSatuan;

            cout << "\nTotal kalori untuk " << jumlahMakanan << " " << jenisMakanan << " adalah " << totalKalori << " kalori." << std::endl;

            if (totalKalori < 500) {
                cout << "Ini adalah makanan ringan dengan sedikit kalori, Bagus untuk camilan!" << endl;

            } else if (totalKalori >= 500 && totalKalori <= 1000) {
                cout << "Makanan ini memiliki jumlah kalori yang cukup, Nikmatilah dengan bijak!" << endl;

            } else {
                cout << "Ini adalah makanan tinggi kalori, Perhatikan asupan kalori harian Anda!" << endl;
            }

            break;

        case 3:
            cout << "\n=====ANDA MEMILIH UNTUK CEK BERAT BADAN=====\n";
            cout << "\nMasukkan tinggi badan Anda (cm) : ";
            cin >> tinggi;

            beratIdeal = (tinggi - 100) - ((tinggi - 100) * 0.1);

            cout << "Berat badan ideal Anda adalah " << beratIdeal << " kg" << endl;

            break;

        case 4:
            cout << "Terima kasih telah cek kesehatan di program kami, semoga membantu dan sampai jumpa lagi :)";
            break;

        default:
            cout << "Pilihan tidak valid. Silakan pilih lagi.\n";
        }

        tanyaLanjut();
    } while (true);

    return 0;
}
