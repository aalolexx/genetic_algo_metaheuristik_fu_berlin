class Generation(list):
    def __init__(self, *args):
        super().__init__(*args)

    def set_losses(self):
        #i = 0
        for ind in self:
            ind.set_loss()
            #print(f"calculated ind loss ({i}/{len(self)})")
            #i += 1

    def get_best(self):
        return min(self, key=lambda ind: ind.loss)

    def average_loss(self):
        return sum(ind.loss for ind in self) / len(self)
    
    def dict_all_inds_loss(self):
        losses = []
        for ind in self:
            losses.append({
                "birth_type": ind.birth_type,
                "loss": ind.loss
            })
        return losses