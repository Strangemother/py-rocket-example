

picked up from py10, this method will lean on a stronger stepper with cleverer nodes.

The mountable class has a list of input nodes, populated by graph edges.

The node will announce a change, and the stepper moves this value to the connected nodes, rippling changes. This can be forced or occur naturally.

Every node should be iterated for its step. and emit value changes when the input nodes alter.


## forced

A forced stepper will capture events and move them to the correct next node. The function cannot emit its own actions or events without an initial stepper execution

may be considered as 'stepper first' event handling

## natural

A node may emit events whilst the stepper is accessing another node (or doing nothing). The event is collected by a stepper and moves into the next node.

may be considered as 'node first' event handling

---

# Simplified

Many functions exist to depend upon each other, or execute in isolation.
The connection of the nodes is performed through a graph

+ The stepper _starts_ at a designated node with pre-defined inputs. The stepper executes the node and collects any output.
+ The stepper Pointer proceeds to the next function in the chain. If many functions exist, + the _pointer_ may fork and start a _new_ pointer event chain, originating from the first.

Each node is called with the values from the previous step or user designated arguments.

---

## Attribute and Function Maps

Version 2 may bind attributes through mapping. An "email()" function may expect an address. The previous function may provide a "User" object.

An Attribute map

    START('admin') -> get_user(username):User -> email(address)

Can bind the map `user.email_address` to `address`:

    >>> res = get_user(username)
    (User(100), )
    >>> kw = map_though(get_user, email, res)
    {
        'address': res[0].email_address
    }
    >>> email(**kw)

This will be done through some sort of auto argument mapping, or dictionary map.
The attribute binding map is available on the main machine.


### Function Map

The same applies for _function_ within the executable caller. The calling unit may call upon graph mapped functions of which call to remapped functions:

```py

from mail import mail

def executor(email_address):
    # send an email
    log('sending email to', email_address)
    try:
        mail(email_address)
    except Exception as exc:
        error(exc)
```

Next we can map `log`, `error` optionally `mail`. Consider the dict side load for locals within the executor function:

    {
        log: print
        error: error_node
    }