import click
import fs.osfs
import tilekiln.config
import tilekiln.kiln
import os
import multiprocessing


@click.group()
def cli():
    pass


@cli.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('storage')
@click.option('-d', '--dbname')
@click.option('-h', '--host')
@click.option('-p', '--port')
@click.option('-U', '--username')
@click.option('-c', '--connections', type=click.INT,
              default=multiprocessing.cpu_count())
@click.option('-s', '--chunk-size', type=click.INT)
@click.option('-z', '--min-zoom', type=click.INT, default=0)
@click.option('-Z', '--max-zoom', type=click.INT, default=14)
def area(config, storage, dbname, host, port, username, connections,
         chunk_size, min_zoom, max_zoom):
    '''Generates tiles for an area'''
    # Get the directory the config is in
    full_path = os.path.join(os.getcwd(), config)
    root_path = os.path.dirname(full_path)
    config_path = os.path.relpath(full_path, root_path)

    filesystem = fs.osfs.OSFS(root_path)

    config = tilekiln.config.Config(filesystem.open(config_path).read(),
                                    filesystem)
    dbinfo = {"dbname": dbname, "host": host, "port": port,
              "username": username}

    tiles = [(z, x, y) for z in range(min_zoom, max_zoom + 1)
             for x in range(2**z) for y in range(2**z)]

    # Apply some heuristics to guess a chunk size
    if chunk_size is None:
        chunk_size = int(min(max(len(tiles)/(2*connections), 10), 50000))

    kiln = tilekiln.kiln.Kiln(config, dbinfo, storage)
    kiln.generate_tiles(tiles, connections, chunk_size)