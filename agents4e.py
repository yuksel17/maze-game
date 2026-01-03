import random
import copy
import collections

# ______________________________________________________________________________

class Thing:
    """Ortamda (Environment) var olabilen her fiziksel nesneyi temsil eder."""

    def __repr__(self):
        # Nesnenin sınıf adını gösterir.
        return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

    def is_alive(self):
        """'Canlı' olan şeylerin True döndürdüğü metot."""
        return hasattr(self, 'alive') and self.alive

class Agent(Thing):
    """
    Ortamdan algı (percept) alan ve aksiyon (action) döndüren bir Thing alt sınıfıdır.
    .program: Ajana ne yapacağını söyleyen fonksiyondur (A* algoritmamız olabilir.).
    """

    def __init__(self, program=None):
        self.alive = True
        self.performance = 0 # Performans ölçütü (Ergonomik maliyetin tersi olabilir)
        # Eğer geçerli bir program yoksa, kullanıcıdan girdi ister (manuel mod)
        if program is None or not isinstance(program, collections.abc.Callable):
            print("Geçerli bir program bulunamadı.")
            def program(percept):
                return eval(input('Algı={}; Aksiyon? '.format(percept)))

        self.program = program

    def can_grab(self, thing):
        """Bu ajan bu nesneyi alabilir mi? (Gitar için pek geçerli değil.)"""
        return False
    
# ______________________________________________________________________________

def TraceAgent(agent):
    """
    Ajanın programını sarmalar ve her adımda girdi/çıktıyı konsola yazdırır.
    (Debugging ve A* adım takibi için çok önemlidir.)
    """
    old_program = agent.program

    def new_program(percept):
        action = old_program(percept)
        # Ajana ne algıladı ve ne yaptı
        print('{} algıladı {} ve şunu yaptı {}'.format(agent, percept, action)) 
        return action

    agent.program = new_program
    return agent

# ______________________________________________________________________________

def RandomAgentProgram(actions):
    """
    Gelen algıları yok sayarak rastgele aksiyon seçen program (Basitlik için).
    """
    return lambda percept: random.choice(actions)

# ______________________________________________________________________________

def ModelBasedReflexAgentProgram(rules, update_state, model):
    """
    [EN ÖNEMLİ BÖLÜM] Algı, durum ve DÜNYA MODELİNİ kullanan ajan programı.
     A* çözümümüzün çerçevesi budur.
    """

    def program(percept):
        # 1. Durumu Güncelle: Algıya göre iç modelini (state) değiştir.
        # Bu adım, A* arama motorunun çalıştırıldığı yerdir.
        program.state = update_state(program.state, program.action, percept, model) 
        
        # 2. Kural Eşleştirme: Yeni duruma göre kuralı (aksiyonu) seç.
        rule = rule_match(program.state, rules)
        action = rule.action
        return action

    program.state = program.action = None
    return program

def rule_match(state, rules):
    """Verilen duruma uyan ilk kuralı bulur."""
    # Basitlik adına, burada kural olarak aksiyonun kendisini döndürdüğünü varsayalım.
    # Gerçek A* uygulamasında 'search.py' doğrudan aksiyon dizisini hesaplar.
    return rules[0] # Örnek kural seçimi

# ______________________________________________________________________________

class Environment:
    """Ortamı (Gitar Klavyesi) temsil eden temel soyut sınıf."""

    def __init__(self):
        self.things = [] # Ortamdaki tüm nesneler (Notlar, Teller)
        self.agents = [] # Ortamdaki tüm ajanlar (Sol El/Parmaklar)

    def percept(self, agent):
        """Ajanın gördüğü algıyı döndürür. (Gitar için: Sıradaki Nota)."""
        raise NotImplementedError

    def execute_action(self, agent, action):
        """Aksiyonun (Parmak Hareketinin) ortamdaki etkisini uygular."""
        raise NotImplementedError

    def step(self):
        """Ortamı bir zaman adımı (bir nota) çalıştırır."""
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.is_alive():
                    # Ajanın programını çalıştırıp aksiyonu al
                    actions.append(agent.program(self.percept(agent)))
                else:
                    actions.append("")
            
            # Aksiyonları sırayla uygula
            for (agent, action) in zip(self.agents, actions):
                self.execute_action(agent, action)

    def is_done(self):
        """Simülasyonun bitip bitmediğini kontrol eder (Riff bitti mi?)."""
        return not any(agent.is_alive() for agent in self.agents)

    def run(self, steps=1000):
        """Ortamı belirli sayıda adım çalıştırır."""
        for step in range(steps):
            if self.is_done():
                return
            self.step()
    
    def add_thing(self, thing, location=None):
        """Ortama yeni bir nesne (agent/thing) ekler."""
        if not isinstance(thing, Thing):
            thing = Agent(thing)
        if thing in self.things:
            print("Aynı nesne iki kez eklenemez")
        else:
            # Burası önemlidir: Ajanı Agents listesine ekler.
            self.things.append(thing)
            if isinstance(thing, Agent):
                thing.performance = 0
                self.agents.append(thing)
                
   