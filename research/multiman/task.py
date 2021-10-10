# An example of a loadout task

class GoToWork(Procedure):
    """Group many actions into one flow.
    """

    # This event can be cancelled.
    can_cancel = True


class Kitchen(Asset):
    """A Unit of values to call upon within the sourcing tree.
    A Kitchen contains "food" for a character to navigate to
    """

    has = (
        'food',
        )


class DoShower(Procedure):

    def processes(self):
        # navigate to bathroom
        navigate_to('bathroom')
        # get undressed
        perform_task('undress')
        # start shower
        navigate_to(find_closest('shower', 'power'))
        perform_task('hit_button', 'power') # within area
        # get in shower
        navigate_to(find_closest('shower'))
        # scrub scrub
        perform_task('scrub self', energy=2, time_taken=120) #secs
        # turn off shower
        navigate_to(find_closest('shower', 'power'))
        perform_task('hit_button', 'power') # within area
        # get out shower
        # dry-self
        perform_task('dry self', time_taken=120) # within area


class EatBreakfast(Procedure):

    def processes(self):
        """Run the eat breakfast procedure"""
        self.navigate_to_kitchen()
        meal = self.make_cereal()
        self.eat_cereal(meal)

    def navigate_to_kitchen(self)
        local_food_source = find_closest('food')
        # Go find food - e.g. Kitchen
        navigate_to(local_food_source)

    def make_cereal(self):
        # Create a meal consisting of cereal
        # must be within food prep room
        return Food(name='cereal', energy=10)

    def eat_cereal(self, meal):
        # Take some time to consume the prepared meal
        perform_task('eating', meal)
