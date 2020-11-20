import os
import shutil

from helper.domain import get_domain
from helper.load import load_all_groups, get_all_sub_kw, get_kw_data
from helper.sanitize_url import sanitize_url
from helper.to_dict import to_dict
from jinja2 import Environment, FileSystemLoader

from sitemap import generate_sitemap

for domain in get_domain():

    all = load_all_groups()

    template_env = Environment(loader=FileSystemLoader(searchpath='./templates'))
    template = template_env.get_template('index.html')

    root_page = ''
    # root_page = f'/generator/example/layout/{domain}'
    root_path = f'layout/{domain}'
    if not os.path.isdir(root_path):
        os.mkdir(root_path)

    # Copy assets directory to root of domain
    shutil.copytree('./templates/assets', f'{root_path}/assets')

    with open(f'layout/{domain}/index.html', 'w') as output_file:
        output_file.write(
            template.render(
                all_data=all,
                sanitize_url=sanitize_url,
                domain=domain,
                root_page=root_page
            )
        )

    """
    Create pages for the individual categories
    """
    template = template_env.get_template('category.html')
    for each in all:
        root = sanitize_url(each['category'])

        path = f'layout/{domain}/{root}'
        if not os.path.isdir(path):
            os.mkdir(path)

        # Copy assets directory to category page
        shutil.copytree('templates/subassets', f'{path}/assets')

        with open(f'{path}/index.html', 'w') as output_file:
            output_file.write(
                template.render(
                    category=each['category'],
                    subcategory=each['subcategory'],
                    get_kw=get_all_sub_kw,
                    sanitize_url=sanitize_url,
                    domain=domain,
                    root_page=root_page
                )
            )


    """
    Create pages for the corresponding Subcategories
    """
    template_env = Environment(loader=FileSystemLoader(searchpath='./templates'))
    template = template_env.get_template('subcategory.html')

    for each in all:
        root = sanitize_url(each['category'])

        path = f'layout/{domain}/{root}'

        for sub in each['subcategory'][0:10]:
            sub_url = sanitize_url(sub)
            subpath = f'{path}/{sub_url}'
            if not os.path.isdir(subpath):
                os.mkdir(subpath)

            # Copy assets directory to category page
            shutil.copytree('templates/subsubassets', f'{subpath}/assets')

            kw_data = get_all_sub_kw(sub)
            with open(f'{subpath}/index.html', 'w') as output_file:
                output_file.write(
                    template.render(
                        category=each['category'],
                        subcateg=sub,
                        kw_data=kw_data,
                        length=len(kw_data['keywords']),
                        sanitize_url=sanitize_url,
                        domain=domain,
                        root_page=root_page
                    )
                )

            """
            Create the details page for the keywords
            """
            template_env = Environment(loader=FileSystemLoader(searchpath='./templates'))
            kw_template = template_env.get_template('details.html')
            for kw in kw_data['keywords']:
                kw_path = f'{subpath}/{sanitize_url(kw)}'
                if not os.path.isdir(kw_path):
                    os.mkdir(kw_path)

                shutil.copytree('./templates/details', f'{kw_path}/assets')

                with open(f'{kw_path}/index.html', 'w') as output_file:
                    output_file.write(
                        kw_template.render(
                            category=each['category'],
                            subcateg=sub,
                            allsub=each['subcategory'][0:10],
                            kw_details=[x for x in get_kw_data(kw)],
                            sanitize_url=sanitize_url,
                            domain=domain,
                            keyword=kw,
                            to_dict=to_dict,
                            root_page=root_page
                        )
                    )

    # Impressum
    impressum_path = f'{root_path}/impressum'
    if not os.path.isdir(impressum_path):
        os.mkdir(impressum_path)
    shutil.copytree('./templates/impressum', f'{impressum_path}/impressum_files')

    impressum_tmp = template_env.get_template('impressum.html')
    with open(f'layout/{domain}/impressum/index.html', 'w') as output_file:
        output_file.write(
            impressum_tmp.render(
                domain=domain
            )
        )

    # Datenschutz
    datenschutz_path = f'{root_path}/datenschutz'
    if not os.path.isdir(datenschutz_path):
        os.mkdir(datenschutz_path)
    shutil.copytree('./templates/datenschutz', f'{datenschutz_path}/datenschutz_files')

    datenschutz_tmp = template_env.get_template('datenschutz.html')
    with open(f'layout/{domain}/datenschutz/index.html', 'w') as output_file:
        output_file.write(
            datenschutz_tmp.render(
                domain=domain
            )
        )

    # Generate Sitemap
    generate_sitemap(f'http://{domain}', all)