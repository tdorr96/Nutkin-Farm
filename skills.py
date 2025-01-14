class Skill:

    def __init__(self, name):

        self.name = name

        self.xp = 0
        self.level = 1
        self.next_level_xp = 100

    def add_xp(self, xp):

        self.xp += xp

        while self.xp >= self.next_level_xp:
            self.level += 1
            self.next_level_xp *= 2


class Skills:

    def __init__(self):

        self.all_skills = ['Woodcutting', 'Farming']
        self.skills = {skill: Skill(skill) for skill in self.all_skills}

    def add_xp(self, skill, xp):

        self.skills[skill].add_xp(xp)

    def get_xp(self, skill):

        return self.skills[skill].xp

    def get_level(self, skill):

        return self.skills[skill].level

    def get_all_vars(self):

        return {
            skill: {'xp': self.get_xp(skill), 'level': self.get_level(skill)}
            for skill in self.all_skills
        }
