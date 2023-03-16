import flags as _flags

from absl import flags
from collections import namedtuple
import torch
from torch import nn, optim
from torch.optim import lr_scheduler as opt_sched
from torch.nn.utils.clip_grad import clip_grad_norm_
from torchdec import hlog
from torchdec.seq import batch_seqs

FLAGS = flags.FLAGS
flags.DEFINE_integer("n_epochs", 512, "number of training epochs")
flags.DEFINE_integer("n_epoch_batches", 32, "batches per epoch")
flags.DEFINE_integer("n_batch", 64, "batch size")
flags.DEFINE_float("lr", 0.001, "learning rate")
flags.DEFINE_float("clip", 1., "gradient clipping")
flags.DEFINE_float("sched_factor", 0.5, "opt scheduler reduce factor")

FLAGS = flags.FLAGS

Datum = namedtuple(
    "Datum", 
    "inp out inp_data out_data direct_out_data copy_out_data extra"
)

def make_batch(samples, vocab, staged):
    device = _flags.device()
    seqs = zip(*samples)
    if staged:
        ref, tgt, *extra = seqs
        (ref_inp, ref_out) = zip(*ref)
        (inp, out) = zip(*tgt)
        ref_inp_data, ref_out_data, inp_data, out_data = (
            batch_seqs(seq).to(device) for seq in (ref_inp, ref_out, inp, out)
        )
        return Datum(
            (ref_inp, ref_out), (inp, out), (ref_inp_data, ref_out_data), 
            (inp_data, out_data), None, None, extra
        )
    else:
        inp, out, *extra = seqs
        inp_data = batch_seqs(inp).to(device)
        out_data = batch_seqs(out).to(device)

        direct_out = []
        copy_out = []
        for i, o in zip(inp, out):
            cout = [tok if tok in i[1:-1] else vocab.pad() for tok in o[1:-1]]
            copy_out.append([o[0]] + cout + [o[-1]])
            dout = [vocab.copy() if tok in i[1:-1] else tok for tok in o[1:-1]]
            direct_out.append([o[0]] + dout + [o[-1]])
        direct_out_data = batch_seqs(direct_out).to(device)
        copy_out_data = batch_seqs(copy_out).to(device)
        #direct_out_data = None
        return Datum(
            inp, out, inp_data, out_data, direct_out_data, copy_out_data, extra
        )
        #copy_out_data = None

@hlog.fn("train")
def train(dataset, model, sample, callback, staged):
    if not isinstance(model, nn.Module):
        return

    opt = optim.Adam(model.parameters(), lr=FLAGS.lr)
    #sched = opt_sched.CosineAnnealingLR(opt, T_max=FLAGS.n_epochs)
    if FLAGS.sched_factor < 1:
        sched = opt_sched.ReduceLROnPlateau(opt, mode='max', factor=FLAGS.sched_factor, verbose=True)

    for i_epoch in hlog.loop("%05d", range(FLAGS.n_epochs)):
        model.train()
        epoch_loss = 0
        for i_batch in range(FLAGS.n_epoch_batches):
            #sched.step()
            opt.zero_grad()
            datum = make_batch(
                [sample() for _ in range(FLAGS.n_batch)], dataset.vocab, staged
            )
            loss = model(
                datum.inp_data, datum.out_data, 
                datum.direct_out_data, datum.copy_out_data,
                *datum.extra
            )
            loss.backward()
            clip_grad_norm_(model.parameters(), FLAGS.clip)
            opt.step()
            epoch_loss += loss.item()
        epoch_loss /= FLAGS.n_epoch_batches
        hlog.value("loss", epoch_loss)
        val_score = callback(i_epoch)
        if FLAGS.sched_factor < 1:
            sched.step(val_score)
