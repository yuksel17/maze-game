"""
CSP (Constraint Satisfaction Problems) - Kısıt Tatmin Problemleri
ve Çözücüleri. (Gitar Projesi İçin Sadeleştirilmiş Versiyon)

İçerik:
1. CSP Temel Sınıfı (Problemin Tanımı)
2. AC3 (Arc Consistency - Yay Tutarlılığı) Algoritması
3. Backtracking Search (Geri İzleme Araması)
4. Min-Conflicts (Yerel Arama / Local Search)
"""

import itertools
import random
import re
import string
from collections import defaultdict, Counter
from functools import reduce
from operator import eq, neg

# Sıralı kümeler için (pip install sortedcontainers gerekebilir, yoksa set kullanılabilir)
from sortedcontainers import SortedSet

import search
from utils4e import argmin_random_tie, count, first, extend

# ______________________________________________________________________________
# 1. TEMEL CSP SINIFI

class CSP(search.Problem):
    """
    Sonlu alanlı (finite-domain) Kısıt Tatmin Problemlerini tanımlayan sınıf.

    Bir CSP şu bileşenlerden oluşur:
    - variables (değişkenler): Değer atanacak nesneler listesi.
    - domains (alanlar): Her değişkenin alabileceği olası değerler {var: [değerler]}.
    - neighbors (komşular): Hangi değişkenin hangisiyle kısıtı olduğunu tutan çizge {var: [var...]}.
    - constraints (kısıtlar): İki değişkenin değerlerinin uyumlu olup olmadığını kontrol eden fonksiyon.
    """

    def __init__(self, variables, domains, neighbors, constraints):
        """CSP problemini başlatır. Değişkenler boşsa, domain anahtarlarını kullanır."""
        super().__init__(()) # search.Problem sınıfını başlat

        # Değişkenleri ayarla (Eğer verilmediyse domain'den al)
        variables = variables or list(domains.keys())
        self.variables = variables

        # Her değişkenin alabileceği değerler kümesi (Domain)
        self.domains = domains

        # Hangi değişkenin hangisiyle ilişkisi (kısıtı) var? (Komşuluk Listesi)
        self.neighbors = neighbors

        # Kısıt kontrol fonksiyonu: f(A, a, B, b) -> True/False
        self.constraints = constraints

        # Şu anki geçerli domainler (Budama/Pruning sırasında güncellenir)
        self.curr_domains = None

        # Yapılan atama sayısı (Performans ölçümü için)
        self.nassigns = 0

    def assign(self, var, val, assignment):
        """
        Bir değişkene bir değer atar.
        assignment: {değişken: değer} sözlüğü.
        """
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """
        Yapılan atamayı geri alır (Backtracking için gerekli).
        """
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """
        Eğer 'var' değişkenine 'val' değerini verirsek,
        şu anki atamalarla kaç tane çakışma (conflict) yaşanır?
        """
        def conflict(var2):
            # Komşu değişkene (var2) bir değer atanmış mı?
            # Ve eğer atanmışsa, bizim değerimizle (val) kısıtı sağlıyor mu?
            # Sağlamıyorsa (not constraints) bu bir çakışmadır.
            return var2 in assignment and not self.constraints(var, val, var2, assignment[var2])

        # Tüm komşuları gez ve çakışmaları say
        return count(conflict(v) for v in self.neighbors[var])

    def display(self, assignment):
        """Mevcut atamaları okunaklı bir şekilde yazdırır."""
        print(assignment)

    # --- Arama Algoritmaları İçin Gerekli Metotlar ---

    def actions(self, state):
        """
        Mevcut durumda yapılabilecek hamleleri döndürür.
        (Henüz atanmamış bir değişken için çakışmayan değerler)
        """
        # Eğer atama sayısı değişken sayısına eşitse, iş bitmiştir.
        if len(state) == len(self.variables):
            return []
        else:
            # Mevcut durumu sözlüğe çevir
            assignment = dict(state)

            # Henüz atanmamış ilk değişkeni bul
            var = first([v for v in self.variables if v not in assignment])

            # Bu değişkenin domainindeki değerlerden, çakışma yaratmayanları döndür
            return [(var, val) for val in self.domains[var]
                    if self.nconflicts(var, val, assignment) == 0]

    def result(self, state, action):
        """
        Bir aksiyonu (atamayı) uygular ve yeni durumu döndürür.
        state: Mevcut atamalar (tuple of tuples)
        action: (değişken, değer)
        """
        (var, val) = action
        # Tuple immutabledır, yeni bir tuple oluşturup ekliyoruz
        return state + ((var, val),)

    def goal_test(self, state):
        """
        Hedefe ulaştık mı?
        1. Tüm değişkenlere değer atanmış olmalı.
        2. Hiçbir çakışma (conflict) olmamalı.
        """
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    # --- Kısıt Yayılımı (Constraint Propagation) Metotları ---

    def support_pruning(self):
        """
        Domain budama (pruning) işlemini başlatmak için yapıyı hazırlar.
        """
        if self.curr_domains is None:
            # Orijinal domainlerin bir kopyasını al, üzerinde değişiklik yapacağız
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """
        Bir varsayım yap: 'var' değişkeni kesinlikle 'value' olsun.
        Diğer tüm ihtimalleri bu değişkenin domaininden kaldır.
        """
        self.support_pruning()
        # Kaldırılacak değerleri listele (ileride geri almak gerekebilir)
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        # Domaini sadece seçilen değere indirge
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        """
        Belirli bir değeri, değişkenin domaininden sil (Budama).
        """
        self.curr_domains[var].remove(value)
        if removals is not None:
            # Silineni kaydet ki backtracking yaparken geri yükleyebilelim
            removals.append((var, value))

    def choices(self, var):
        """
        Bir değişken için elenmemiş, hala mümkün olan değerleri döndür.
        """
        return (self.curr_domains or self.domains)[var]

    def infer_assignment(self):
        """
        Mevcut çıkarımlara göre kesinleşmiş atamaları döndür.
        (Eğer bir değişkenin domaininde tek bir değer kaldıysa, o kesinleşmiştir)
        """
        self.support_pruning()
        return {v: self.curr_domains[v][0]
                for v in self.variables if 1 == len(self.curr_domains[v])}

    def restore(self, removals):
        """
        Yapılan budamaları geri al (Backtracking sırasında kullanılır).
        """
        for B, b in removals:
            self.curr_domains[B].append(b)

    def conflicted_vars(self, current):
        """
        Mevcut atamada çakışma yaratan değişkenlerin listesini döndür.
        (Min-Conflicts algoritması için gerekli)
        """
        return [var for var in self.variables
                if self.nconflicts(var, current[var], current) > 0]


# ______________________________________________________________________________
# 2. AC3 (ARC CONSISTENCY) ALGORİTMASI
# Yay (Arc) tutarlılığını sağlayarak domainleri daraltır.

def no_arc_heuristic(csp, queue):
    return queue

def dom_j_up(csp, queue):
    # Kuyruğu domain boyutuna göre sıralar (Verimlilik için)
    return SortedSet(queue, key=lambda t: neg(len(csp.curr_domains[t[1]])))

def AC3(csp, queue=None, removals=None, arc_heuristic=dom_j_up):
    """
    [Figure 6.3] AC-3 Algoritması.
    Kısıtları kontrol ederek imkansız değerleri domainlerden siler.
    Eğer bir değişkenin domaini boşalırsa, çözüm imkansızdır (False döner).
    """
    # Eğer kuyruk verilmediyse, tüm komşuluk ilişkilerini (yayları) ekle
    if queue is None:
        queue = {(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]}

    csp.support_pruning()
    queue = arc_heuristic(csp, queue)
    checks = 0

    while queue:
        # Kuyruktan bir yay (Xi, Xj) al
        (Xi, Xj) = queue.pop()

        # Xi'nin domainini Xj'ye göre revize et (uyumsuzları sil)
        revised, checks = revise(csp, Xi, Xj, removals, checks)

        if revised:
            # Eğer Xi'nin domaini tamamen boşaldıysa, çözüm yoktur.
            if not csp.curr_domains[Xi]:
                return False, checks  # CSP tutarsız (inconsistent)

            # Xi değiştiği için, onun komşularını da tekrar kontrol etmeliyiz
            for Xk in csp.neighbors[Xi]:
                if Xk != Xj:
                    queue.add((Xk, Xi))

    return True, checks  # CSP tutarlı (satisfiable)


def revise(csp, Xi, Xj, removals, checks=0):
    """
    Xi değişkeninin domainindeki değerlerden, Xj ile uyumsuz olanları siler.
    """
    revised = False
    # Xi'nin tüm olası değerleri için döngü
    for x in csp.curr_domains[Xi][:]:
        conflict = True
        # Xj'nin domaininde, x ile uyumlu EN AZ BİR değer (y) var mı?
        for y in csp.curr_domains[Xj]:
            if csp.constraints(Xi, x, Xj, y):
                conflict = False # Uyumlu bir değer bulundu, x güvende.
            checks += 1
            if not conflict:
                break

        # Eğer x için Xj'de hiç uyumlu değer yoksa, x'i sil.
        if conflict:
            csp.prune(Xi, x, removals)
            revised = True

    return revised, checks


# ______________________________________________________________________________
# 3. BACKTRACKING SEARCH (GERİ İZLEME ARAMASI)
# CSP'leri çözmek için en temel ve yaygın algoritma.

# --- Değişken Seçim Stratejileri ---

def first_unassigned_variable(assignment, csp):
    """Varsayılan: Sıradaki ilk atanmamış değişkeni seç."""
    return first([var for var in csp.variables if var not in assignment])

def mrv(assignment, csp):
    """
    Minimum Remaining Values (En Az Kalan Değer) Sezgisi.
    Domaininde en az değer kalmış (en kritik) değişkeni seçer.
    """
    return argmin_random_tie([v for v in csp.variables if v not in assignment],
                             key=lambda var: num_legal_values(csp, var, assignment))

def num_legal_values(csp, var, assignment):
    """Bir değişken için kaç yasal değer kaldığını sayar."""
    if csp.curr_domains:
        return len(csp.curr_domains[var])
    else:
        return count(csp.nconflicts(var, val, assignment) == 0 for val in csp.domains[var])

# --- Değer Seçim Stratejileri ---

def unordered_domain_values(var, assignment, csp):
    """Varsayılan: Değerleri rastgele/sırasız döndür."""
    return csp.choices(var)

def lcv(var, assignment, csp):
    """
    Least Constraining Value (En Az Kısıtlayıcı Değer).
    Diğer değişkenleri en az kısıtlayan değeri önce dener.
    """
    return sorted(csp.choices(var), key=lambda val: csp.nconflicts(var, val, assignment))

# --- Çıkarım (Inference) Yöntemleri ---

def no_inference(csp, var, value, assignment, removals):
    """Hiçbir ileriye dönük kontrol yapma."""
    return True

def forward_checking(csp, var, value, assignment, removals):
    """
    İleriye Bakma (Forward Checking).
    Atanan değer ile uyumsuz olan komşu değerleri siler.
    Eğer bir komşunun domaini boşalırsa, bu atama yanlıştır (False).
    """
    csp.support_pruning()
    for B in csp.neighbors[var]:
        if B not in assignment:
            for b in csp.curr_domains[B][:]:
                if not csp.constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                return False
    return True

def mac(csp, var, value, assignment, removals, constraint_propagation=AC3):
    """
    MAC (Maintaining Arc Consistency).
    Her atamadan sonra AC3 algoritmasını çalıştırarak tam tutarlılık sağlar.
    """
    return constraint_propagation(csp, {(X, var) for X in csp.neighbors[var]}, removals)

# --- Ana Arama Fonksiyonu ---

def backtracking_search(csp, select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values, inference=no_inference):
    """
    [Figure 6.5] Backtracking Search Algoritması.
    Derinlemesine arama yaparak değişkenlere değer atar.
    Çıkmaza girerse geri döner (backtrack).
    """

    def backtrack(assignment):
        # 1. Eğer atamalar tamamsa, çözümü döndür.
        if len(assignment) == len(csp.variables):
            return assignment

        # 2. Atanmamış bir değişken seç (Sezgilere göre)
        var = select_unassigned_variable(assignment, csp)

        # 3. Bu değişken için değerleri dene
        for value in order_domain_values(var, assignment, csp):
            # Eğer değer çakışma yaratmıyorsa
            if 0 == csp.nconflicts(var, value, assignment):
                # Değeri ata
                csp.assign(var, value, assignment)

                # Budama listesini hazırla (inference için)
                removals = csp.suppose(var, value)

                # Çıkarım yap (Forward Checking veya MAC)
                if inference(csp, var, value, assignment, removals):
                    # Recursive olarak devam et
                    result = backtrack(assignment)
                    if result is not None:
                        return result

                # Eğer buraya geldiysek atama başarısızdır, geri al (Restore)
                csp.restore(removals)

        # Değişkenin atamasını kaldır ve geri dön (Backtrack)
        csp.unassign(var, assignment)
        return None

    # Boş atama ile başla
    result = backtrack({})
    assert result is None or csp.goal_test(result)
    return result


# ______________________________________________________________________________
# 4. MIN-CONFLICTS (YEREL ARAMA)
# Başlangıçta rastgele dağıtıp, hataları düzelterek ilerleyen hızlı bir yöntem.

def min_conflicts(csp, max_steps=100000):
    """
    [Figure 6.8] Min-Conflicts Algoritması.
    Büyük N-Queens problemleri gibi problemler için çok hızlıdır.
    """
    # 1. Tüm değişkenlere rastgele ama "en az kötü" değerleri ata
    csp.current = current = {}
    for var in csp.variables:
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)

    # 2. Belirli bir adım sayısı kadar döngüye gir
    for i in range(max_steps):
        # Çakışma yaşayan değişkenleri bul
        conflicted = csp.conflicted_vars(current)

        # Eğer çakışma yoksa çözüm bulunmuştur!
        if not conflicted:
            return current

        # Çakışanlardan rastgele birini seç
        var = random.choice(conflicted)

        # Bu değişkenin değerini, çakışmayı en aza indirecek şekilde değiştir
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)

    return None # Çözüm bulunamadı

def min_conflicts_value(csp, var, current):
    """
    Bir değişken için, mevcut durumda en az çakışma yaratan değeri döndürür.
    """
    return argmin_random_tie(csp.domains[var], key=lambda val: csp.nconflicts(var, val, current))

# ______________________________________________________________________________
# YARDIMCI SINIFLAR VE FONKSİYONLAR

class UniversalDict:
    """
    Her anahtar için aynı değeri döndüren bir sözlük.
    Tüm değişkenlerin domaini aynı olduğunda bellek tasarrufu sağlar.
    """
    def __init__(self, value): self.value = value
    def __getitem__(self, key): return self.value
    def __repr__(self): return '{{Any: {0!r}}}'.format(self.value)

def parse_neighbors(neighbors):
    """
    'X: Y Z; Y: Z' formatındaki stringi komşuluk sözlüğüne çevirir.
    Gitar klavyesinde bunu elle yapmak yerine matematiksel hesaplayacağız,
    ama genel CSP'ler için kullanışlıdır.
    """
    dic = defaultdict(list)
    specs = [spec.split(':') for spec in neighbors.split(';')]
    for (A, Aneighbors) in specs:
        A = A.strip()
        for B in Aneighbors.split():
            dic[A].append(B)
            dic[B].append(A)
    return dic