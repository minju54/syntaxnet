#!/usr/bin/env python
#-*- coding: utf8 -*-
import sys
import os
import time
import tensorflow as tf
import model_dragnn as model

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('dragnn_spec', '', 
                    'Path to the spec defining the model.')
flags.DEFINE_string('resource_path', '',
                    'Path to constructed resources.')
flags.DEFINE_string('checkpoint_filename', '',
                    'Filename to save the best checkpoint to.')
flags.DEFINE_bool('enable_tracing', False, 
                    'Whether tracing annotations')
 
def main(unused_argv) :

    if len(sys.argv) == 1 :
        flags._global_parser.print_help()
        sys.exit(0)

    # Loading model
    sess, graph, builder, annotator = model.load_model(FLAGS.dragnn_spec,
                                             FLAGS.resource_path,
                                             FLAGS.checkpoint_filename,
                                             FLAGS.enable_tracing)    

    # Analyze
    startTime = time.time()
    while 1 :
        try : line = sys.stdin.readline()
        except KeyboardInterrupt : break
        if not line : break
        line = line.strip()
        if not line : continue
        sentence = model.inference(sess, graph, builder, annotator, line, FLAGS.enable_tracing)
        f = sys.stdout
        f.write('# text = ' + line.encode('utf-8') + '\n')
        for i, token in enumerate(sentence.token) :
            head = token.head + 1
            attributed_tag = token.tag.encode('utf-8')
            attr_dict = model.attributed_tag_to_dict(attributed_tag)
            fPOS = attr_dict['fPOS']
            tag = fPOS.replace('++',' ').split()
            label = token.label.encode('utf-8').split(':')[0]
            f.write('%s\t%s\t%s\t%s\t%s\t_\t%d\t%s\t_\t_\n'%(
                i + 1,
                token.word.encode('utf-8'),
                token.word.encode('utf-8'),
                tag[0],
                tag[1],
                head,
                label))
        f.write('\n\n')
    durationTime = time.time() - startTime
    sys.stderr.write("duration time = %f\n" % durationTime)

    # Close session
    sess.close()
    
if __name__ == '__main__':
    tf.app.run()

